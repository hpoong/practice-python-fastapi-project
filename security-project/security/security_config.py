from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from core.exceptions import unauthorized_response

class GlobalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/login"):
            return await call_next(request)
        token = request.headers.get("Authorization")
        if not token:
            return unauthorized_response("Token empty.")
        return await call_next(request)
