import sys
from unittest.mock import MagicMock

# Attempt to mock taskiq if it is not installed
try:
    import taskiq
except ImportError:
    # Create a mock for taskiq module
    taskiq_mock = MagicMock()
    sys.modules["taskiq"] = taskiq_mock

    # Mock InMemoryBroker class
    class MockInMemoryBroker:
        def __init__(self, *args, **kwargs):
            self.is_worker_process = False

        def task(self, *args, **kwargs):
            # Handle @broker.task and @broker.task(...)
            def decorator(func):
                # The wrapper should behave like the original function but also have taskiq attributes
                def wrapper(*f_args, **f_kwargs):
                    return func(*f_args, **f_kwargs)

                # Mock typical taskiq task methods
                wrapper.kiq = MagicMock()
                return wrapper

            if len(args) == 1 and callable(args[0]) and not kwargs:
                return decorator(args[0])
            return decorator

        async def startup(self):
            pass

        async def shutdown(self):
            pass

    # Assign the mock class to the module
    taskiq_mock.InMemoryBroker = MockInMemoryBroker

# Mock pydantic if missing
try:
    import pydantic
except ImportError:
    pydantic_mock = MagicMock()
    sys.modules["pydantic"] = pydantic_mock
    # partial mock for BaseModel
    class MockBaseModel:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    pydantic_mock.BaseModel = MockBaseModel

# Mock fastapi if missing
try:
    import fastapi
except ImportError:
    fastapi_mock = MagicMock()
    sys.modules["fastapi"] = fastapi_mock

# Mock lancedb if missing
try:
    import lancedb
except ImportError:
    lancedb_mock = MagicMock()
    sys.modules["lancedb"] = lancedb_mock

# Mock pyarrow if missing
try:
    import pyarrow
except ImportError:
    pyarrow_mock = MagicMock()
    pyarrow_mock.schema = MagicMock()
    pyarrow_mock.field = MagicMock()
    sys.modules["pyarrow"] = pyarrow_mock
