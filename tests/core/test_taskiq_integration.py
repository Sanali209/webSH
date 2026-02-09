import pytest
from core.sdk import PluginContext
from core.broker import broker

def test_background_task_integration():
    """Verify that background_task correctly wraps function with broker.task"""
    context = PluginContext(plugin_id="test_plugin")

    # Define a task
    @context.background_task
    def my_bg_task(arg):
        return arg * 2

    # Check if it has taskiq attributes (mocked in conftest or real)
    # If real taskiq is installed, it has kiq. If mocked, we added kiq.
    assert hasattr(my_bg_task, "kiq")

    # Check execution
    assert my_bg_task(10) == 20

def test_broker_lifecycle_mock():
    """Verify broker has startup/shutdown methods (mocked or real)"""
    assert hasattr(broker, "startup")
    assert hasattr(broker, "shutdown")

    # Check for is_worker_process attribute
    assert hasattr(broker, "is_worker_process")
