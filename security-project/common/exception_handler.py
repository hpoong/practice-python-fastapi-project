from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from common.service_type_enum import ServiceTypeEnum
from response.error_response import ErrorResponse
import logging
from fastapi import HTTPException

logger = logging.getLogger("uvicorn.error")

def add_exception_handlers(app: FastAPI):
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error("HTTPException", exc_info=exc)
        error_response = ErrorResponse.with_message(
            service_type=ServiceTypeEnum.SERVER,
            message=str(exc.detail)
        )
        return JSONResponse(status_code=exc.status_code, content=error_response.dict())