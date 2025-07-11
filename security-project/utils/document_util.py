import re
import tiktoken

class DocumentUtil:
    """
    문서 전처리 및 chunking 담당 클래스.
    """

    def __init__(self, max_tokens: int = 500, encoding_name: str = "cl100k_base"):
        """
        초기화 메서드.
        :param max_tokens: 각 chunk의 최대 토큰 수
        :param encoding_name: 사용할 tokenizer 이름 (기본: cl100k_base, OpenAI 최신 tokenizer)
        """
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding(encoding_name)


    def clean_text(self, text: str) -> str:
        """
        기본적인 전처리 함수.
        HTML 태그, 여러 공백 제거 등.
        """
        text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
        text = re.sub(r'\s+', ' ', text)     # 여러 공백을 하나로
        text = text.strip()
        return text

    def split_into_sentences(self, text: str) -> list:
        """
        문장을 기준으로 분할.
        영어 기준 기본 패턴, 한글 포함 시 추가 커스터마이즈 가능.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences

    def chunk_sentences(self, sentences: list) -> list:
        """
        여러 문장을 합쳐서 chunk를 생성.
        각 chunk의 토큰 개수가 max_tokens를 넘지 않도록 제한.
        """
        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = len(self.tokenizer.encode(sentence))

            if current_tokens + sentence_tokens <= self.max_tokens:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_tokens = sentence_tokens

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def preprocess(self, document_text: str) -> list:
        """
        전체 전처리 및 chunking 실행 함수.
        :param document_text: 원본 문서 텍스트
        :return: chunk 리스트
        """
        cleaned = self.clean_text(document_text)
        sentences = self.split_into_sentences(cleaned)
        chunks = self.chunk_sentences(sentences)
        return chunks
