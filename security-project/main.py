from fastapi import FastAPI
# from core.security import GlobalAuthMiddleware
# from routers import user_router, admin_router
from fastapi.middleware.cors import CORSMiddleware

from common.exception_handler import add_exception_handlers
from common.service_type_enum import ServiceTypeEnum
from response.common_response import CommonResponse
from response.success_response import SuccessResponse
from fastapi import HTTPException
# from security.security_config import GlobalAuthMiddleware

app = FastAPI()


add_exception_handlers(app)

# app.add_middleware(GlobalAuthMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def printHello():
    return CommonResponse(
        success=True,
        serviceType=ServiceTypeEnum.USER,
        message="User Service Test",
    )

@app.get("/success")
def success_example():
    return SuccessResponse.with_data(
        service_type=ServiceTypeEnum.USER,
        message="성공적으로 처리되었습니다.",
        data={"example": "데이터 예시"}
    )

@app.get("/error")
def error_example():
    raise HTTPException(status_code=400, detail="일부러 발생시킨 에러입니다.")


# Routers
# app.include_router(user_router.router)
# app.include_router(admin_router.router)