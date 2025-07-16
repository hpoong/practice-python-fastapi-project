from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from common.service_type_enum import ServiceTypeEnum
from exception.exception_handler import add_exception_handlers
from response.success_response import SuccessResponse
from security.security_config import GlobalAuthMiddleware
from db.pinecone_client import index

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
            "category": {"$in": ["news", "blog"]}
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

    return SuccessResponse.with_message(
        service_type=ServiceTypeEnum.SERVER,
        message="프롬프트 생성이 완료되었습니다."
    )