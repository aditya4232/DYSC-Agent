import json
import ipaddress
import os
import re
from urllib.parse import urlparse

from .paths import PROVIDERS_FILE


def _read():
    return json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))


def _write(payload):
    PROVIDERS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def list_providers():
    data = _read()
    return data


def _validate_base_url(provider_id, base_url):
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Provider base_url must use http or https")
    if not parsed.hostname:
        raise ValueError("Provider base_url must include a valid hostname")

    allow_local = provider_id == "local-ollama"
    host = parsed.hostname.lower()

    if host in {"localhost", "127.0.0.1", "::1"}:
        if not allow_local:
            raise ValueError("Localhost providers are restricted to local-ollama")
        return

    try:
        ip = ipaddress.ip_address(host)
        if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved) and not allow_local:
            raise ValueError("Private or reserved network hosts are blocked for this provider id")
    except ValueError:
        return


def add_provider(provider_id, provider_type, base_url, api_key_env, enabled):
    if not provider_id or not provider_type or not base_url or not api_key_env:
        raise ValueError("Provider fields cannot be empty")

    _validate_base_url(provider_id, base_url)

    data = _read()
    existing = [p for p in data["providers"] if p["id"] == provider_id]
    if existing:
        raise ValueError(f"Provider already exists: {provider_id}")

    provider = {
        "id": provider_id,
        "type": provider_type,
        "base_url": base_url,
        "api_key_env": api_key_env,
        "enabled": bool(enabled),
    }
    data["providers"].append(provider)
    _write(data)
    return provider


def set_primary_provider(provider_id):
    data = _read()
    if not any(p["id"] == provider_id for p in data["providers"]):
        raise ValueError(f"Provider not found: {provider_id}")
    data["primary"] = provider_id
    _write(data)


def set_provider_key_env(provider_id, api_key_env):
    if not re.fullmatch(r"[A-Z_][A-Z0-9_]{0,127}", api_key_env):
        raise ValueError("api_key_env must be a valid environment variable name")

    data = _read()
    provider = next((p for p in data["providers"] if p["id"] == provider_id), None)
    if provider is None:
        raise ValueError(f"Provider not found: {provider_id}")
    provider["api_key_env"] = api_key_env
    _write(data)
    return provider


def provider_key_status(provider_id):
    data = _read()
    provider = next((p for p in data["providers"] if p["id"] == provider_id), None)
    if provider is None:
        raise ValueError(f"Provider not found: {provider_id}")

    env_name = provider.get("api_key_env")
    value = os.environ.get(env_name, "")
    return {
        "provider": provider_id,
        "api_key_env": env_name,
        "present": bool(value),
    }
