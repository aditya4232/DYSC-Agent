import json
from pathlib import Path

from .chat_store import ChatStore
from .paths import CHAT_DB_FILE, CONFIG_DIR, DATA_DIR, PROVIDERS_FILE, SETTINGS_FILE, SKILLS_DIR, SKILLS_FILE, WORKSPACES_FILE
from .settings import DEFAULT_SETTINGS


DEFAULT_PROVIDERS = {
    "primary": "local-ollama",
    "providers": [
        {
            "id": "local-ollama",
            "type": "openai_compatible",
            "base_url": "http://localhost:11434/v1",
            "api_key_env": "OLLAMA_API_KEY",
            "enabled": True,
        }
    ],
}

DEFAULT_WORKSPACES = {
    "primary": str(Path.cwd()),
    "known": [str(Path.cwd())],
}

DEFAULT_SKILLS = {
    "enabled": ["builtin.security-review", "builtin.bug-hunt"],
    "installed": [
        {
            "id": "builtin.security-review",
            "source": "builtin",
            "path": "skills/builtin/security-review.skill.json",
        },
        {
            "id": "builtin.bug-hunt",
            "source": "builtin",
            "path": "skills/builtin/bug-hunt.skill.json",
        },
    ],
}


def _write_json_if_missing(target, payload):
    if not target.exists():
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ensure_bootstrap():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (SKILLS_DIR / "builtin").mkdir(parents=True, exist_ok=True)
    (SKILLS_DIR / "installed").mkdir(parents=True, exist_ok=True)
    (SKILLS_DIR.parent / "skills-imports").mkdir(parents=True, exist_ok=True)

    _write_json_if_missing(PROVIDERS_FILE, DEFAULT_PROVIDERS)
    _write_json_if_missing(WORKSPACES_FILE, DEFAULT_WORKSPACES)
    _write_json_if_missing(SKILLS_FILE, DEFAULT_SKILLS)
    _write_json_if_missing(SETTINGS_FILE, DEFAULT_SETTINGS)

    ChatStore().initialize()

    return {
        "config": str(CONFIG_DIR),
        "data": str(DATA_DIR),
        "skills": str(SKILLS_DIR),
        "chat_db": str(CHAT_DB_FILE),
    }
