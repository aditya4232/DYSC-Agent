# DYSC Agent (Hybrid CLI + Runtime)

DYSC is a non-web coding agent scaffold with:

- Multi-provider API setup with primary provider selection
- Primary workspace folder management
- Skills registry (built-in + additional local installs)
- Claude-Code-style security review and AI fix suggestion flows
- Real-time dependency/context snapshot (manifests + Python packages)
- Green-signal startup readiness checks
- Local backend chat persistence with SQLite

## Architecture

- Node CLI: `apps/cli/main.js`
- Python runtime: `apps/agent-runtime/main.py`
- Runtime modules: `apps/agent-runtime/dysc_runtime/`
- Config files: `config/`
- Persistent data: `data/`
- Skills files: `skills/`


## Quick Start

### Install like a global CLI

Install globally from the project root:

```powershell
npm install -g .
```

Or run the installer script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1
```

Then run DYSC directly:

```powershell
dysc health
dysc start
```

### 1) Initialize project state

```powershell
node apps/cli/main.js init
```

This creates default config and local DB schema.

### 2) Configure providers (single or multiple)

List providers:

```powershell
node apps/cli/main.js provider list
```

Add a provider:

```powershell
node apps/cli/main.js provider add --id groq-main --type provider_specific --base-url https://api.groq.com/openai/v1 --api-key-env GROQ_API_KEY --enabled true
```

Set primary provider:

```powershell
node apps/cli/main.js provider set-primary groq-main
```

### 3) Set primary workspace folder

```powershell
node apps/cli/main.js workspace set D:/Spicyepanda-24-26/xystocode26/AI-26/DYSC-Agent-
```

### 4) Manage skills

List skills:

```powershell
node apps/cli/main.js skills list
```

Enable a skill:

```powershell
node apps/cli/main.js skills enable builtin.security-review
```

Install an additional local skill JSON:

```powershell
node apps/cli/main.js skills install-local custom.fixstyle D:/Spicyepanda-24-26/xystocode26/AI-26/DYSC-Agent-/skills-imports/custom.fixstyle.json
```

Security note: local skill imports are restricted to the `skills-imports/` folder.

### 5) Start DYSC agent with green signal

```powershell
node apps/cli/main.js start
```

If all checks pass, DYSC prints:

```text
🟢 DYSC READY
```

The process remains active until you stop it (`Ctrl + C`).

For one-time readiness verification:

```powershell
node apps/cli/main.js start --once
```

### 6) Real-time context and security review

Get current dependency/runtime context:

```powershell
node apps/cli/main.js context packages
```

Run automated security review:

```powershell
node apps/cli/main.js review security --limit 200
```

Generate a human-robust fix plan for a finding:

```powershell
node apps/cli/main.js fix suggest --file apps/agent-runtime/main.py --line 120 --rule PY-EVAL-001 --snippet "eval(user_input)"
```

### 7) Save and read chat history (backend SQLite)

Save message:

```powershell
node apps/cli/main.js chat save --session demo --role user --content "scan this repo"
```

List session messages:

```powershell
node apps/cli/main.js chat list demo
```

## Notes

- DYSC supports both OpenAI-compatible and provider-specific adapters in config.
- API keys are referenced by environment variable names (no plaintext secrets in config).
- Offline mode works with local endpoints (example: Ollama-compatible base URL).
