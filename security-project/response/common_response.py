from pydantic import BaseModel, Field
from common.service_type_enum import ServiceTypeEnum
from utils.time_util import TimeUtil


class CommonResponse(BaseModel):
    success: bool
    serviceType: ServiceTypeEnum
    message: str
    timestamp: str = Field(default_factory=TimeUtil.get_unix_timestamp_ms)
    serviceName: str = "security-service"  # TODO : service명 작성

    class Config:
        use_enum_values = True
