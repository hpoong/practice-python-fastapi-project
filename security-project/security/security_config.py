from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from security.auth_entry_point import unauthorized_response


class GlobalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/login"):
            return await call_next(request)
        token = request.headers.get("Authorization")
        if not token:
            return unauthorized_response()
        return await call_next(request)
