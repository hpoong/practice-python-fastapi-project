import json
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from common.service_type_enum import ServiceTypeEnum
from exception.exception_handler import add_exception_handlers
from response.success_response import SuccessResponse
from security.security_config import GlobalAuthMiddleware
from db.pinecone_client import index
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
                "category": "news"
            }
        }

        vectors.append(vector_data)

    # 5. JSON 파일로 저장
    with open("vector_chunks.json", "w", encoding="utf-8") as f:
        json.dump(vectors, f, ensure_ascii=False, indent=2)

    return SuccessResponse.with_message(
        service_type=ServiceTypeEnum.SERVER,
        message="vector_chunks.json 파일이 성공적으로 생성되었습니다."
    )