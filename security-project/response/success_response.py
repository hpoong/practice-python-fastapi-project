from response.common_response import CommonResponse
from pydantic import Field
from typing import Any, Optional
from common.service_type_enum import ServiceTypeEnum

class SuccessResponse(CommonResponse):
    data: Optional[Any] = None
    code: Optional[str] = None

    @classmethod
    def with_data(cls, service_type: ServiceTypeEnum, message: str, data: Any = None):
        return cls(
            success=True,
            serviceType=service_type,
            message=message,
            data=data
        )

    @classmethod
    def with_message(cls, service_type: ServiceTypeEnum, message: str):
        return cls.with_data(
            service_type=service_type,
            message=message,
            data=None
        )

    @classmethod
    def success_with_data(cls, service_type: ServiceTypeEnum, data: Any):
        return cls.with_data(
            service_type=service_type,
            message="Success",
            data=data
        )