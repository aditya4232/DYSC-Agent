import json
import os
import urllib.request
import urllib.error

from .providers import list_providers
from .settings import list_settings

def get_primary_provider():
    data = list_providers()
    primary_id = data.get("primary")
    if not primary_id:
        return None
    for p in data.get("providers", []):
        if p["id"] == primary_id:
            return p
    return None

def chat_completion(messages, tools=None):
    provider = get_primary_provider()
    if not provider:
        raise ValueError("No primary provider configured")
    
    if not provider.get("enabled"):
        raise ValueError(f"Primary provider {provider['id']} is disabled")

    base_url = provider["base_url"].rstrip("/")
    api_key_env = provider["api_key_env"]
    api_key = os.environ.get(api_key_env, "dummy-key") # Ollama doesn't need a real key

    url = f"{base_url}/chat/completions"
    
    settings = list_settings()
    default_model = settings.get("default_model", "llama3")
    model = default_model

    payload = {
        "model": model,
        "messages": messages,
    }
    
    if tools:
        payload["tools"] = tools

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode("utf-8"), 
        headers=headers, 
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"LLM API Error ({e.code}): {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to connect to LLM provider: {e.reason}")
