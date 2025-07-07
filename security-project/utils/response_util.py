from fastapi import Response
import json

class ResponseUtil:

    @staticmethod
    def send_json_response(status_code: int, result: dict) -> Response:
        content = json.dumps(result, ensure_ascii=False)
        return Response(
            content=content,
            status_code=status_code,
            media_type="application/json",
            headers={"Content-Type": "application/json; charset=utf-8"}
        )