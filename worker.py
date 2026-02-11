import sys
import os

# Ensure proper path
sys.path.insert(0, os.getcwd())

from core.executor import broker

# Import the backend module to ensure the @broker.task decorator is executed
# and the task is registered with the broker.
import plugins.system_executor.backend

# The 'broker' variable here is what 'taskiq worker worker:broker' will use.
