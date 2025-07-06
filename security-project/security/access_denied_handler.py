from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def forbidden_response(detail: str = "Role empty."):
    content = {"code": "SECURITY_LOGIN", "message": detail}
    return JSONResponse(status_code=480, content=content)
