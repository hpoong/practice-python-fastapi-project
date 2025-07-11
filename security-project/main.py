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
        message="성공적으로 처리되었습니다.",
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

class ServerSearchRequest(BaseModel):
    query: str
    top_k: int = 5



@app.post("search")
async def search(request: ServerSearchRequest):
    """SentenceTransformer로 임베딩 후 Pinecone에서 검색하는 엔드포인트"""

    query_text = request.query
    top_k = request.top_k

    print(query_text)

    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    query_embedding = model.encode(query_text).tolist()

    # Pinecone에서 검색
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={
            "category": {"$nin": ["news", "blog"]}
        }
    )

    print(result)

    

@app.get("/embedding")
async def embedding(request: Request):
    # 1. 문서 원문
    document_text = """
    """

    # 2. 문단 단위 청크 분리 (빈 줄 기준 or 문장 기준 분할 가능)
    chunks = re.split(r'\n+', document_text.strip())
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    # 3. 모델 로드
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')  # 예시 한국어 모델

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

    print("vector_chunks.json 파일 생성 완료! (청크 단위)")



@app.get("/chunks")
async def chunks(request: Request):
    
    example_text = """
    <h1>API 인증 설명</h1>
    This API allows you to authenticate users via OAuth2. It requires a client_id and client_secret.
    If authentication fails, it returns a 401 status code. You must also provide a redirect_uri
    when initiating the authentication flow. Users will be redirected to the given URL after
    successful login. Make sure to securely store the client_secret. Revoke tokens if you suspect
    any compromise. OAuth2 is a standard protocol for authorization and is widely used
    in modern applications. Always follow security best practices when implementing OAuth2.
    """

    # 인스턴스 생성 (max_tokens 예: 50으로 설정)
    preprocessor = DocumentUtil(max_tokens=50)

    # 전처리 및 chunking
    chunks = preprocessor.preprocess(example_text)

    # 출력
    for i, chunk in enumerate(chunks, 1):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()