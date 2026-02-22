from importlib import metadata
from pathlib import Path

from .workspace import show_workspace


MANIFEST_FILES = [
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "go.mod",
    "Cargo.toml",
]


def _workspace_root():
    workspace = show_workspace()
    return Path(workspace).resolve() if workspace else Path.cwd().resolve()


def _discover_manifests(root):
    manifests = []
    for relative in MANIFEST_FILES:
        candidate = root / relative
        if candidate.exists() and candidate.is_file():
            manifests.append(str(candidate.relative_to(root)).replace("\\", "/"))
    return manifests


def _python_packages(limit=80):
    items = []
    for dist in metadata.distributions():
        name = dist.metadata.get("Name")
        version = dist.version
        if not name:
            continue
        items.append({"name": name, "version": version})

    items.sort(key=lambda item: item["name"].lower())
    return items[:limit]


def get_runtime_context():
    root = _workspace_root()
    manifests = _discover_manifests(root)
    packages = _python_packages()

    return {
        "ok": True,
        "workspace": str(root),
        "dependency_manifests": manifests,
        "python_packages_count": len(packages),
        "python_packages": packages,
        "note": "Use this snapshot before review/fix to keep context current.",
    }
