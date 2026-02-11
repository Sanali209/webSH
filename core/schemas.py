from pydantic import BaseModel, Field, ConfigDict
from typing import Any, List, Optional, Dict
import uuid
from datetime import datetime

class Context(BaseModel):
    caller_id: str
    token: Optional[str] = None
    parent_id: Optional[str] = None
    trace_stack: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

class CapabilityEnvelope(BaseModel):
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str
    params: Dict[str, Any] = Field(default_factory=dict)
    context: Context

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
