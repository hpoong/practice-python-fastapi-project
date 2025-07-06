from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def unauthorized_response(detail: str = "Token empty."):
    content = {"code": "SECURITY_LOGIN", "message": detail}
    return JSONResponse(status_code=480, content=content)


