# DYSC Setup Guide

## Requirements

- Node.js 18+
- Python 3.10+

## Install as CLI command

```powershell
npm install -g .
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1
```

After install, use `dysc` directly (example: `dysc health`).

## Onboard

```powershell
dysc onboard
```

## Initialize

```powershell
node apps/cli/main.js init
```

## Multi-API Setup

DYSC supports:

- `openai_compatible` providers (custom base URLs)
- `provider_specific` adapters (explicit provider identity)


Add providers:

```powershell
dysc provider add --id openrouter --type openai_compatible --base-url https://openrouter.ai/api/v1 --api-key-env OPENROUTER_API_KEY --enabled true
dysc provider add --id groq-main --type provider_specific --base-url https://api.groq.com/openai/v1 --api-key-env GROQ_API_KEY --enabled true
```

Set primary provider:

```powershell
dysc provider set-primary openrouter
```

Secure API key setup (key stays in env only):

```powershell
dysc provider set-key-env openrouter OPENROUTER_API_KEY
setx OPENROUTER_API_KEY "<your_key_here>"
dysc provider key-status openrouter
```

## Primary Workspace Folder

```powershell
dysc workspace set D:/Spicyepanda-24-26/xystocode26/AI-26/DYSC-Agent-
```

Open any local project:

```powershell
dysc workspace open D:/path/to/your/local-project
```

Use current terminal project folder:

```powershell
dysc workspace use-current
```

DYSC auto-uses current project as default if previously configured workspace is missing.

## Skills

Built-in skills are pre-registered. Add local skill JSON:

```powershell
dysc skills install-local custom.patch-tone D:/Spicyepanda-24-26/xystocode26/AI-26/DYSC-Agent-/skills-imports/custom.patch-tone.json
```

Local skill import is restricted to the `skills-imports/` directory.

Enable/disable skills:

```powershell
dysc skills enable custom.patch-tone
dysc skills disable custom.patch-tone
```

## Start and Green Signal

```powershell
dysc start
```

If readiness checks pass, DYSC emits `🟢 DYSC READY`.

`start` stays active until stopped (`Ctrl + C`).

For one-time readiness check only:

```powershell
dysc start --once
```

## Claude-Code-Style Security Workflows

Get real-time runtime and package context:

```powershell
dysc context packages
```

Run automated security review:

```powershell
dysc review security --limit 200
```

Generate robust fix guidance for any finding:

```powershell
dysc fix suggest --file apps/agent-runtime/main.py --line 120 --rule PY-EVAL-001 --snippet "eval(user_input)"
```

## Settings

```powershell
dysc settings show
dysc settings set default_model llama3
dysc settings set max_tool_rounds 6
```

## Chat Backend Persistence

Save:

```powershell
dysc chat save --session demo --role user --content "run secure review"
```

Read:

```powershell
dysc chat list demo
```

Slash commands in interactive runtime:

```text
/help /health /review [limit] /context /settings /providers /workspace /skills /exit
```

Stored in `data/chat.db`.
