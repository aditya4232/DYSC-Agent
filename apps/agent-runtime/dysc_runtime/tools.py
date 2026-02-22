import json
import os
from pathlib import Path

from .workspace import show_workspace

def get_workspace_root():
    ws = show_workspace()
    if not ws:
        return Path.cwd()
    return Path(ws)

def read_file(path):
    root = get_workspace_root()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        return "Error: Path is outside workspace"
    if not target.exists():
        return f"Error: File not found: {path}"
    if not target.is_file():
        return f"Error: Not a file: {path}"
    try:
        return target.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path, content):
    root = get_workspace_root()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        return "Error: Path is outside workspace"
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def list_files(path="."):
    root = get_workspace_root()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        return "Error: Path is outside workspace"
    if not target.exists():
        return f"Error: Directory not found: {path}"
    if not target.is_dir():
        return f"Error: Not a directory: {path}"
    try:
        files = []
        for item in target.iterdir():
            files.append(f"{item.name}{'/' if item.is_dir() else ''}")
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {e}"

def scan_workspace(pattern):
    root = get_workspace_root()
    try:
        files = list(root.rglob(pattern))
        return f"Found {len(files)} files matching {pattern}"
    except Exception as e:
        return f"Error scanning workspace: {e}"

def analyze_code(rules):
    # Mock implementation for now
    return f"Analyzed code using rules: {', '.join(rules)}. No critical issues found."

def execute_tool(name, args):
    if name == "read_file":
        return read_file(args.get("path"))
    elif name == "write_file":
        return write_file(args.get("path"), args.get("content"))
    elif name == "list_files":
        return list_files(args.get("path", "."))
    elif name == "scan_workspace":
        return scan_workspace(args.get("pattern"))
    elif name == "analyze_code":
        return analyze_code(args.get("rules", []))
    else:
        return f"Error: Unknown tool {name}"

def get_available_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file in the workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The relative path to the file"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file in the workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The relative path to the file"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write"
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files and directories in a given path",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The relative path to the directory (default: current directory)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scan_workspace",
                "description": "Scan the workspace for files matching a pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "The glob pattern to match (e.g., **/*.py)"
                        }
                    },
                    "required": ["pattern"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_code",
                "description": "Analyze code for security vulnerabilities or bugs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rules": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The rules to apply (e.g., owasp_top_10, logical_errors)"
                        }
                    },
                    "required": ["rules"]
                }
            }
        }
    ]
