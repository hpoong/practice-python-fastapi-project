from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key = api_key)

all_indexes = pc.list_indexes()
print("현재 사용 가능한 Index 목록:", all_indexes)

index = pc.Index(index_name)
print(f"Index 객체 준비 완료: {index_name}")


try:
    stats = index.describe_index_stats()
    print(f"'{index_name}' index 연결 및 상태 확인 완료!")
except Exception as e:
    print(f"Index 연결 상태 확인 실패: {e}")



__all__ = ["index"]