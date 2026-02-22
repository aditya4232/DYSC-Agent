import json
import re
from pathlib import Path

from .paths import SKILLS_DIR, SKILLS_FILE


def _read():
    return json.loads(SKILLS_FILE.read_text(encoding="utf-8"))


def _write(payload):
    SKILLS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def list_skills():
    return _read()


def _validate_skill_id(skill_id):
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", skill_id):
        raise ValueError("Invalid skill id format")


def _imports_root():
    return (SKILLS_DIR.parent / "skills-imports").resolve()


def _validate_skill_payload(payload, skill_id):
    required = ["id", "name", "description", "triggers", "steps"]
    for field in required:
        if field not in payload:
            raise ValueError(f"Skill JSON missing field: {field}")
    if payload["id"] != skill_id:
        raise ValueError("Skill id mismatch between argument and JSON content")
    if not isinstance(payload["triggers"], list) or not isinstance(payload["steps"], list):
        raise ValueError("Skill triggers and steps must be arrays")


def enable_skill(skill_id):
    data = _read()
    if skill_id not in data.get("enabled", []):
        data.setdefault("enabled", []).append(skill_id)
    _write(data)
    return data["enabled"]


def disable_skill(skill_id):
    data = _read()
    data["enabled"] = [item for item in data.get("enabled", []) if item != skill_id]
    _write(data)
    return data["enabled"]


def install_local_skill(skill_id, json_path):
    _validate_skill_id(skill_id)

    imports_root = _imports_root()
    imports_root.mkdir(parents=True, exist_ok=True)

    source = Path(json_path).expanduser().resolve()
    if not source.exists() or source.suffix.lower() != ".json":
        raise ValueError(f"Invalid skill file path: {source}")

    if imports_root not in source.parents:
        raise ValueError(f"Skill import must come from: {imports_root}")

    payload = json.loads(source.read_text(encoding="utf-8"))
    _validate_skill_payload(payload, skill_id)

    target = SKILLS_DIR / "installed" / f"{skill_id}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    data = _read()
    data["installed"] = [entry for entry in data.get("installed", []) if entry.get("id") != skill_id]
    installed = {
        "id": skill_id,
        "source": "local",
        "path": str(target.relative_to(SKILLS_DIR.parent)).replace("\\", "/"),
    }
    data["installed"].append(installed)
    if skill_id not in data.get("enabled", []):
        data.setdefault("enabled", []).append(skill_id)
    _write(data)
    return installed
