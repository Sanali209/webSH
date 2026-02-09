from pydantic import BaseModel
from typing import List

class FSSettings(BaseModel):
    root_path: str = "."
    excluded_dirs: List[str] = [".git", "node_modules", ".venv", "__pycache__", "dist", ".idea", ".vscode"]
