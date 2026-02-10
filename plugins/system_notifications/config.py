from pydantic import BaseModel, Field

class NotificationSettings(BaseModel):
    enabled: bool = Field(True, description="Enable notifications")
    timeout: int = Field(5000, description="Toast timeout in ms")
