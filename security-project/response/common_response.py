from pydantic import BaseModel, Field

from utils.time_util import TimeUtil


class CommonResponse(BaseModel):
    success: bool
    type: str
    code: str
    message: str
    timestamp: str = Field(default_factory=TimeUtil.get_unix_timestamp_ms())
    serviceName: str = "security-project-service"

    def __init__(self, **data):
        super().__init__(**data)