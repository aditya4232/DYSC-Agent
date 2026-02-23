import json
from pathlib import Path

from .paths import WORKSPACES_FILE


def _read():
    return json.loads(WORKSPACES_FILE.read_text(encoding="utf-8"))


def _write(payload):
    WORKSPACES_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def show_workspace():
    return _read()


def get_primary_workspace():
    data = _read()
    return data.get("primary")


def get_effective_workspace():
    primary = get_primary_workspace()
    if primary:
        try:
            path = Path(primary)
            if path.exists() and path.is_dir():
                return str(path.resolve())
        except OSError:
            pass
    return str(Path.cwd().resolve())


def ensure_workspace_default_to_cwd(force=False):
    data = _read()
    current = str(Path.cwd().resolve())
    primary = data.get("primary")

    primary_missing = not primary
    primary_invalid = False
    if primary:
        try:
            primary_invalid = not Path(primary).exists()
        except OSError:
            primary_invalid = True

    if force or primary_missing or primary_invalid:
        data["primary"] = current

    if current not in data.get("known", []):
        data.setdefault("known", []).append(current)

    _write(data)
    return data


def set_workspace(folder_path):
    resolved = Path(folder_path).expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"Workspace path does not exist: {resolved}")
    if not resolved.is_dir():
        raise ValueError(f"Workspace path must be a directory: {resolved}")

    data = _read()
    normalized = str(resolved)
    data["primary"] = normalized
    if normalized not in data.get("known", []):
        data.setdefault("known", []).append(normalized)
    _write(data)
    return data
