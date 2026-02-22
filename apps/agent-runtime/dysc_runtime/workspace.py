import json
from pathlib import Path

from .paths import WORKSPACES_FILE


def _read():
    return json.loads(WORKSPACES_FILE.read_text(encoding="utf-8"))


def _write(payload):
    WORKSPACES_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def show_workspace():
    return _read()


def set_workspace(folder_path):
    resolved = Path(folder_path).expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"Workspace path does not exist: {resolved}")

    data = _read()
    normalized = str(resolved)
    data["primary"] = normalized
    if normalized not in data.get("known", []):
        data.setdefault("known", []).append(normalized)
    _write(data)
    return data
