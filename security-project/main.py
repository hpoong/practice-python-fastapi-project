import json
import uuid

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from common.service_type_enum import ServiceTypeEnum
from exception.business_exception import BusinessException
from exception.exception_handler import add_exception_handlers
from response.common_response import CommonResponse
from response.success_response import SuccessResponse
from security.security_config import GlobalAuthMiddleware
from db.pinecone_client import index
from sentence_transformers import SentenceTransformer
import numpy as np
import re
from utils.document_util import DocumentUtil

app = FastAPI()


add_exception_handlers(app)

app.add_middleware(GlobalAuthMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
def printHello():
    return CommonResponse(
        success=True,
        serviceType=ServiceTypeEnum.SERVER,
        message="login test",
    )

@app.get("/success")
def success_example():
    return SuccessResponse.with_data(
        service_type=ServiceTypeEnum.SERVER,
        data={"example": "데이터 예시"}
    )

@app.get("/error")
def error_example():
    raise BusinessException(
        message="일부러 발생시킨 에러입니다.",
        service_type=ServiceTypeEnum.SERVER
    )

@app.get("/profile")
async def read_profile(request: Request):
    if not hasattr(request.state, "user"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = request.state.user
    return {
        "message": f"Hello {user['user_id']} with role {user['user_role']}"
    }

@app.get("/upsert")
async def upsert(request: Request):
    # vector_chunks.json 파일 읽기
    with open("vector_chunks.json", "r", encoding="utf-8") as f:
        vectors = json.load(f)

    # Pinecone에 upsert
    index.upsert(vectors=vectors)
    return SuccessResponse.with_message(
        service_type=ServiceTypeEnum.SERVER,
        message="vector_chunks.json 기반 벡터 upsert 완료!"
    )


@app.get("/embedding")
async def embedding(request: Request):
    # 1. 문서 원문
    document_text = """
    """

    # 2. DocumentUtil을 사용한 청크 분리
    preprocessor = DocumentUtil(max_tokens=50)  # 원하는 token 크기
    chunks = preprocessor.preprocess(document_text)

    # 3. 모델 로드
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')  # 한국어 예시

    # 4. 각 청크에 대해 임베딩 생성 및 JSON 데이터 준비
    vectors = []
    document_id = str(uuid.uuid4())

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk)

        vector_data = {
            "id": f"{document_id}#chunk{i}",
            "values": embedding.tolist(),
            "metadata": {
                "text": chunk,
                "chunk_index": i
            }
        }

        vectors.append(vector_data)

    # 5. JSON 파일로 저장
    with open("vector_chunks.json", "w", encoding="utf-8") as f:
        json.dump(vectors, f, ensure_ascii=False, indent=2)

    print("vector_chunks.json 파일 생성 완료! (DocumentUtil 기반 청크)")
    return {"message": "vector_chunks.json 파일이 성공적으로 생성되었습니다."}


# 요청 모델 정의
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):

    # [1] 질문 임베딩
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')  # 한국어 예시 모델
    embedding = model.encode(req.question)
    embedding_list = embedding.tolist()

    # [2] Pinecone에서 검색
    result = index.query(
        vector=embedding_list,
        top_k=5,
        include_metadata=True,
        filter={
            "category": {"$nin": ["news", "blog"]}
        }
    )

    # matches 리스트 가져오기
    matches = result.get('matches', [])

    # text만 리스트로 추출
    texts = [match['metadata'].get('text', '') for match in matches]

    # 만약 검색 결과가 부족하면 빈 문자열로 채움
    if len(texts) < 2:
        texts += [""] * (2 - len(texts))

    # [3] 문서 내용을 하나의 문자열로 합치기
    document_content = "\n".join(texts)

    # [4] LLM 프롬프트 생성
    prompt = f"""
    너는 전문 뉴스 분석가야.
    주어진 뉴스 문서를 분석하고 아래 질문에 객관적이고 정확하게 답변해줘.
    또한, 문서의 핵심 내용을 이해하기 쉽게 요약하고 추가 분석도 포함시켜줘.
    
    다음 형식을 지켜줘:
    
    * 요약: 문서의 핵심 내용을 한 문단으로 요약.
    * 배경 설명: 기사의 맥락과 배경 정보를 포함.
    * 추가 분석: 전문가 시각에서의 분석 및 의미 해석.
    * 향후 전망: 앞으로의 영향이나 가능성.
    
    문서 내용:
    {document_content}
    
    질문: {req.question}
    
    출력은 한글로 작성하고, 정보 왜곡이나 과도한 추측은 피할 것.
    모든 답변은 간결하면서도 핵심적인 내용을 담아야 하며, 불필요한 반복은 하지 마.
    """

    # 디버깅용 출력
    print(prompt)


@app.get("/delete-all")
async def delete_all_vectors():
    namespace_name = ""
    try:
        index.delete(delete_all=True, namespace=namespace_name)
        return {"message": f"Namespace '{namespace_name}'의 모든 vector가 삭제되었습니다."}
    except Exception as e:
        return {"error": str(e)}