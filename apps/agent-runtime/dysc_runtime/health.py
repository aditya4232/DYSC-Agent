import json
from pathlib import Path

from .chat_store import ChatStore
from .paths import PROVIDERS_FILE, SKILLS_FILE, WORKSPACES_FILE


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_health_checks():
    checks = []

    provider_data = _read_json(PROVIDERS_FILE)
    workspace_data = _read_json(WORKSPACES_FILE)
    skills_data = _read_json(SKILLS_FILE)

    primary_provider_id = provider_data.get("primary")
    providers = provider_data.get("providers", [])
    primary_provider = next((item for item in providers if item.get("id") == primary_provider_id), None)

    provider_ok = primary_provider is not None and primary_provider.get("enabled") is True
    checks.append(
        {
            "name": "primary_provider",
            "ok": provider_ok,
            "detail": primary_provider_id if provider_ok else "Primary provider missing or disabled",
        }
    )

    workspace_path = workspace_data.get("primary", "")
    workspace_ok = Path(workspace_path).exists()
    checks.append(
        {
            "name": "workspace",
            "ok": workspace_ok,
            "detail": workspace_path if workspace_ok else "Primary workspace path does not exist",
        }
    )

    enabled_skills = skills_data.get("enabled", [])
    skills_ok = len(enabled_skills) > 0
    checks.append(
        {
            "name": "skills",
            "ok": skills_ok,
            "detail": enabled_skills if skills_ok else "No enabled skills found",
        }
    )

    chat_ok = True
    chat_detail = "chat db ready"
    try:
        ChatStore().initialize()
    except Exception as exc:
        chat_ok = False
        chat_detail = str(exc)
    checks.append(
        {
            "name": "chat_store",
            "ok": chat_ok,
            "detail": chat_detail,
        }
    )

    status = "green" if all(item["ok"] for item in checks) else "red"
    return {
        "status": status,
        "checks": checks,
        "active_provider": primary_provider_id,
        "workspace": workspace_path,
        "enabled_skills": enabled_skills,
    }
