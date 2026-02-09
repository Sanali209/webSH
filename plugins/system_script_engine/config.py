"""
Configuration for Script Engine Plugin.
"""

from core.sdk import PluginSettings


class ScriptEngineSettings(PluginSettings):
    """Settings for the Script Engine plugin."""
    
    # Execution settings
    max_execution_time: int = 300  # seconds
    max_workflow_nodes: int = 100
    max_parallel_nodes: int = 10
    
    # Storage settings
    save_workflows: bool = True
    save_execution_history: bool = True
    max_history_entries: int = 1000
    
    # Security settings
    allow_file_operations: bool = True
    allow_network_operations: bool = True
    allow_system_commands: bool = False
    
    # Performance settings
    cache_node_results: bool = True
    enable_parallel_execution: bool = True
