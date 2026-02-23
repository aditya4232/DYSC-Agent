import json

from .paths import SETTINGS_FILE


DEFAULT_SETTINGS = {
    "default_model": "llama3",
    "max_tool_rounds": 4,
}


ALLOWED_KEYS = {
    "default_model": str,
    "max_tool_rounds": int,
}


def _read():
    return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))


def _write(payload):
    SETTINGS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def list_settings():
    return _read()


def set_setting(key, value):
    if key not in ALLOWED_KEYS:
        raise ValueError(f"Unknown setting: {key}")

    expected_type = ALLOWED_KEYS[key]
    parsed_value = value
    if expected_type is int:
        try:
            parsed_value = int(value)
        except ValueError as exc:
            raise ValueError(f"Setting {key} requires integer value") from exc
        if parsed_value < 1 or parsed_value > 32:
            raise ValueError("max_tool_rounds must be between 1 and 32")
    elif expected_type is str:
        parsed_value = str(value).strip()
        if not parsed_value:
            raise ValueError(f"Setting {key} cannot be empty")

    settings = _read()
    settings[key] = parsed_value
    _write(settings)
    return settings
