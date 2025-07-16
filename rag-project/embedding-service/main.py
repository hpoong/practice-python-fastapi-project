from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.service_type_enum import ServiceTypeEnum
from exception.exception_handler import add_exception_handlers
from response.success_response import SuccessResponse
from security.security_config import GlobalAuthMiddleware

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


@app.get("/")
def success_example():
    return SuccessResponse.with_data(
        service_type=ServiceTypeEnum.SERVER,
        data={"example": "데이터 예시"}
    )
