from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from common.service_type_enum import ServiceTypeEnum
from exception.business_exception import BusinessException
from exception.exception_handler import add_exception_handlers
from response.success_response import SuccessResponse
from security.security_config import GlobalAuthMiddleware

# middleware
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


@app.get("/success")
def success_example():
    return SuccessResponse.with_data(
        service_type=ServiceTypeEnum.SERVER,
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
    return SuccessResponse.with_message(
        service_type=ServiceTypeEnum.SERVER,
        message=f"Hello {user['user_id']} with role {user['user_role']}"
    )