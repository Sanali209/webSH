from pydantic import BaseModel, Field, ConfigDict
from typing import Any, List, Optional, Dict, Literal
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

class WidgetSchema(BaseModel):
    id: str
    size: Literal["1x1", "2x2", "2x1", "4x2"]
    entry_point: str
    title: str
    type: Literal["widget"] = "widget"

    model_config = ConfigDict(extra='forbid')

class TopBarItemSchema(BaseModel):
    id: str
    entry_point: str
    component: Optional[str] = None
    type: Literal["top_bar.item"] = "top_bar.item"

    model_config = ConfigDict(extra='forbid')

class ViewSchema(BaseModel):
    id: str
    title: str
    entry_point: str

    model_config = ConfigDict(extra='forbid')

class ShortcutSchema(BaseModel):
    icon: str
    title: str
    action: str

    model_config = ConfigDict(extra='forbid')

class PluginUI(BaseModel):
    widgets: List[WidgetSchema] = Field(default_factory=list)
    views: List[ViewSchema] = Field(default_factory=list)
    shortcuts: List[ShortcutSchema] = Field(default_factory=list)
    top_bar: List[TopBarItemSchema] = Field(default_factory=list)

class WidgetConfig(BaseModel):
    id: str
    x: int
    y: int
    w: int
    h: int
    type: str
    label: Optional[str] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    props: Optional[str] = None

class DesktopConfig(BaseModel):
    id: int
    widgets: List[WidgetConfig]
