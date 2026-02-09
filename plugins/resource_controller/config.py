"""Configuration for Resource Controller Plugin."""
from pydantic import BaseModel, Field
from core.sdk import PluginSettings


class ResourceSettings(PluginSettings):
    """Settings for the Resource Controller plugin."""
    
    # Quota settings
    max_workers_per_plugin: int = Field(
        default=5,
        description="Maximum concurrent workers per plugin"
    )
    
    max_cpu_percent: float = Field(
        default=80.0,
        description="Maximum CPU usage percentage before throttling"
    )
    
    max_memory_mb: int = Field(
        default=512,
        description="Maximum memory usage in MB per plugin"
    )
    
    # Monitoring settings
    monitoring_interval: int = Field(
        default=5,
        description="Resource monitoring interval in seconds"
    )
    
    enable_auto_throttle: bool = Field(
        default=True,
        description="Automatically throttle plugins exceeding resource limits"
    )
