"""
Workflow nodes for File System plugin.
"""

from pathlib import Path
from typing import List

from core.workflow import workflow_node, NodeInput, NodeOutput


@workflow_node(
    id="fs_read_file",
    name="Read File",
    description="Read contents of a file",
    inputs=[
        NodeInput(name="path", type="string", description="File path to read")
    ],
    outputs=[
        NodeOutput(name="content", type="string", description="File contents")
    ]
)
def read_file(path: str) -> str:
    """Read file contents."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


@workflow_node(
    id="fs_list_files",
    name="List Files",
    description="List files in a directory",
    inputs=[
        NodeInput(name="directory", type="string", description="Directory path")
    ],
    outputs=[
        NodeOutput(name="files", type="list", description="List of file paths")
    ]
)
def list_files(directory: str) -> List[str]:
    """List files in directory."""
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Invalid directory: {directory}")
    
    files = [str(f) for f in dir_path.iterdir() if f.is_file()]
    return files


@workflow_node(
    id="fs_write_file",
    name="Write File",
    description="Write content to a file",
    inputs=[
        NodeInput(name="path", type="string", description="File path to write"),
        NodeInput(name="content", type="string", description="Content to write")
    ],
    outputs=[
        NodeOutput(name="success", type="boolean", description="Write success")
    ]
)
def write_file(path: str, content: str) -> bool:
    """Write content to file."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True
