"""Configuration for System Dashboard Plugin."""
from pydantic import BaseModel, Field
from core.sdk import PluginSettings


class DashboardSettings(PluginSettings):
    """Settings for the Dashboard plugin."""
    
    # Layout configuration
    grid_columns: int = Field(
        default=12,
        description="Number of columns in the dashboard grid"
    )
    
    row_height: int = Field(
        default=60,
        description="Height of each grid row in pixels"
    )
    
    gap: int = Field(
        default=16,
        description="Gap between widgets in pixels"
    )
    
    # Default view
    default_view: bool = Field(
        default=True,
        description="Whether dashboard is the default view on app load"
    )
