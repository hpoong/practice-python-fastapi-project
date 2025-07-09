from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from security.auth_entry_point import unauthorized_response


class GlobalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # 토큰 검사
        if request.url.path.startswith("/login"):
            return await call_next(request)
        # token = request.headers.get("Authorization")
        # if not token:
        #     return unauthorized_response()

        # User 정보
        user_id = request.headers.get("X-User-Id", "test-user")
        user_role = request.headers.get("X-User-Role", "test-role")

        if not user_id or not user_role:
            return unauthorized_response()

        request.state.user = {"user_id": user_id, "user_role": user_role}
        return await call_next(request)
