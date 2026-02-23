from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "config"
DATA_DIR = REPO_ROOT / "data"
SKILLS_DIR = REPO_ROOT / "skills"

PROVIDERS_FILE = CONFIG_DIR / "providers.json"
WORKSPACES_FILE = CONFIG_DIR / "workspaces.json"
SKILLS_FILE = CONFIG_DIR / "skills.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
CHAT_DB_FILE = DATA_DIR / "chat.db"
