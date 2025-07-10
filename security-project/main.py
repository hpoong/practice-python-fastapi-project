import json
import uuid

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.post("/search")
async def search(request: Request):
    body = await request.json()
    query_text = body.get("query")
    top_k = int(body.get("top_k", 5))
    if not query_text:
        raise HTTPException(status_code=400, detail="query 파라미터가 필요합니다.")

    # 1. 쿼리 임베딩 생성
    model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    query_embedding = model.encode(query_text).tolist()

    # 2. (필요시) filter map 읽기
    try:
        with open("metadata.txt", "r", encoding="utf-8") as f:
            filter_map = json.load(f)
    except Exception:
        filter_map = None

    # 3. Pinecone에서 검색
    search_kwargs = {
        "vector": query_embedding,
        "top_k": top_k,
        "include_metadata": True
    }
    if filter_map:
        search_kwargs["filter"] = filter_map

    result = index.query(**search_kwargs)
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