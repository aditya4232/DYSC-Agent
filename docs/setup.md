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
node apps/cli/main.js provider add --id openrouter --type openai_compatible --base-url https://openrouter.ai/api/v1 --api-key-env OPENROUTER_API_KEY --enabled true
node apps/cli/main.js provider add --id groq-main --type provider_specific --base-url https://api.groq.com/openai/v1 --api-key-env GROQ_API_KEY --enabled true
```

Set primary provider:

```powershell
node apps/cli/main.js provider set-primary openrouter
```

## Primary Workspace Folder

```powershell
node apps/cli/main.js workspace set D:/Spicyepanda-24-26/xystocode26/AI-26/DYSC-Agent-
```

## Skills

Built-in skills are pre-registered. Add local skill JSON:

```powershell
node apps/cli/main.js skills install-local custom.patch-tone D:/Spicyepanda-24-26/xystocode26/AI-26/DYSC-Agent-/skills-imports/custom.patch-tone.json
```

Local skill import is restricted to the `skills-imports/` directory.

Enable/disable skills:

```powershell
node apps/cli/main.js skills enable custom.patch-tone
node apps/cli/main.js skills disable custom.patch-tone
```

## Start and Green Signal

```powershell
node apps/cli/main.js start
```

If readiness checks pass, DYSC emits `🟢 DYSC READY`.

`start` stays active until stopped (`Ctrl + C`).

For one-time readiness check only:

```powershell
node apps/cli/main.js start --once
```

## Claude-Code-Style Security Workflows

Get real-time runtime and package context:

```powershell
node apps/cli/main.js context packages
```

Run automated security review:

```powershell
node apps/cli/main.js review security --limit 200
```

Generate robust fix guidance for any finding:

```powershell
node apps/cli/main.js fix suggest --file apps/agent-runtime/main.py --line 120 --rule PY-EVAL-001 --snippet "eval(user_input)"
```

## Chat Backend Persistence

Save:

```powershell
node apps/cli/main.js chat save --session demo --role user --content "run secure review"
```

Read:

```powershell
node apps/cli/main.js chat list demo
```

Stored in `data/chat.db`.
