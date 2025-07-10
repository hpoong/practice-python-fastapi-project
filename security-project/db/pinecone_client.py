from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

index_name = "YOUR_INDEX_NAME"

all_indexes = pc.list_indexes()
print("현재 사용 가능한 Index 목록:", all_indexes)

if index_name in all_indexes:
    print(f" '{index_name}' index가 존재합니다. 연결 성공!")
else:
    print(f" '{index_name}' index가 존재하지 않습니다. 새로 생성합니다...")

index = pc.Index(index_name)
print(f"Index 객체 준비 완료: {index_name}")

__all__ = ["index"]