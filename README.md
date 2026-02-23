<div align="center">

# DYSC Agent

**Security-first coding CLI agent with multi-provider AI, automated vulnerability scanning, and interactive REPL.**

[![npm version](https://img.shields.io/npm/v/dysc-agent?color=cb3837&logo=npm)](https://www.npmjs.com/package/dysc-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?logo=node.js)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org/)

```
      @@@
  @@@@@@@@@@@
 @@@@@@ @@@@@@
@@@@@   *   @@@@@
 @@@@@@ @@@@@@
  @@@@@@@@@@@
      @@@
   DYSC AGENT v0.77
```

</div>

---

## What is DYSC

DYSC is a globally installable CLI agent that combines static security analysis with AI-powered fix suggestions. It connects to any OpenAI-compatible provider (OpenRouter, Groq, Ollama, etc.), manages local workspaces, and offers an interactive REPL with tool-calling and persistent chat.

**Core ideas:**

- API keys stay in OS environment variables — never stored in config files
- Multi-provider setup with primary/fallback selection
- Automated scanning for Python and JavaScript vulnerability patterns
- Human-robust fix plans for every finding
- SQLite-backed chat persistence
- Extensible skills system (built-in + local installs)

---

## Install

**From npm (recommended):**

```bash
npm install -g dysc-agent
```

**From source (contributors):**

```bash
git clone https://github.com/aditya4232/DYSC-Agent-.git
cd DYSC-Agent-
npm install -g .
```

**Verify:**

```bash
dysc health
```

---

## Quick Start

```bash
# 1. Initialize config and workspace
dysc onboard

# 2. Check system readiness
dysc health

# 3. Launch interactive agent
dysc start
```

---

## Command Reference

### Core

| Command | Description |
|---|---|
| `dysc init` | Initialize config files and directories |
| `dysc onboard [path]` | First-time setup with guided configuration |
| `dysc start` | Launch interactive REPL with AI agent |
| `dysc start --once` | Readiness check and exit |
| `dysc health` | Run full system health check |
| `dysc doctor` | Alias for `dysc health` |
| `dysc --version` | Print version |

### Provider and API Security

```bash
dysc provider list
dysc provider add --id <id> --type <openai_compatible|provider_specific> --base-url <url> --api-key-env <ENV> --enabled true
dysc provider set-primary <id>
dysc provider set-key-env <id> <ENV>
dysc provider key-status <id>
```

Set an API key securely (never stored in config files):

```bash
# Linux / macOS
export OPENROUTER_API_KEY="your_key_here"

# Windows (permanent)
setx OPENROUTER_API_KEY "your_key_here"
```

### Workspace Management

```bash
dysc workspace show             # Show current workspace config
dysc workspace set <path>       # Set primary workspace
dysc workspace open <path>      # Open a local project
dysc workspace use-current      # Use terminal's current directory
```

If the configured workspace path is missing or invalid, DYSC falls back to the current working directory automatically.

### Security and Context

```bash
dysc context packages                              # Snapshot runtime dependencies
dysc review security --limit 200                   # Scan workspace for vulnerabilities
dysc fix suggest --file <path> --line <n> --rule <RULE-ID> --snippet "<code>"
```

### Settings

```bash
dysc settings show
dysc settings set default_model llama3
dysc settings set max_tool_rounds 6
```

### Skills

```bash
dysc skills list
dysc skills enable <skillId>
dysc skills disable <skillId>
dysc skills install-local <skillId> <jsonPath>
```

### Chat Persistence

```bash
dysc chat save --session demo --role user --content "scan this repo"
dysc chat list demo
```

---

## Interactive Slash Commands

Inside `dysc start`:

```
/help        Show available commands
/health      Run health checks
/review [n]  Run security review (optional limit)
/context     Show runtime/package context
/settings    Display current settings
/providers   List configured providers
/workspace   Show workspace info
/skills      List skills
/exit        Exit the REPL
```

---

## Project Structure

```
DYSC-Agent-/
├── apps/
│   ├── cli/
│   │   └── main.js                    # Global `dysc` command entry (Node.js)
│   └── agent-runtime/
│       ├── main.py                    # Command dispatcher + interactive REPL
│       └── dysc_runtime/
│           ├── __init__.py            # Package marker + version
│           ├── chat_store.py          # SQLite chat persistence
│           ├── context_runtime.py     # Dependency/manifest discovery
│           ├── health.py              # System health checks
│           ├── llm.py                 # LLM API client (OpenAI-compatible)
│           ├── paths.py               # Centralized path constants
│           ├── providers.py           # Provider registry + URL validation
│           ├── security.py            # Static security scan rules (8 rules)
│           ├── settings.py            # Runtime settings management
│           ├── skills.py              # Skill registry + local install
│           ├── state.py               # Bootstrap + default config creation
│           ├── tools.py               # Filesystem tool-call handlers
│           └── workspace.py           # Workspace state + fallback logic
├── config/
│   ├── providers.json                 # Provider config (gitignored)
│   ├── settings.json                  # Runtime settings (gitignored)
│   ├── skills.json                    # Skills registry (gitignored)
│   ├── workspaces.json                # Workspace paths (gitignored)
│   └── skills/builtin/               # Shipped skill definitions
├── data/
│   └── chat.db                        # SQLite chat database (gitignored)
├── docs/
│   └── setup.md                       # Detailed setup guide
├── scripts/
│   └── install.ps1                    # Windows PowerShell install helper
├── skills/
│   ├── builtin/                       # Source skill asset templates
│   └── installed/                     # User-installed local skills
├── skills-imports/                    # Staging area for local skill imports
├── package.json
├── LICENSE
└── README.md
```

---

## Security Rules

DYSC ships with 8 built-in security rules covering Python and JavaScript:

| Rule ID | Severity | Description |
|---|---|---|
| `PY-EVAL-001` | High | Use of `eval()` — arbitrary code execution |
| `PY-EXEC-001` | High | Use of `exec()` — untrusted code execution |
| `PY-SHELL-001` | High | `shell=True` — command injection risk |
| `PY-REQUESTS-001` | Medium | `verify=False` — TLS verification disabled |
| `PY-HASH-001` | Medium | MD5/SHA1 — weak hash algorithms |
| `JS-EVAL-001` | High | JavaScript `eval()` — unsafe with untrusted input |
| `JS-FUNCTION-001` | High | `new Function()` — dynamic function construction |
| `JS-EXEC-001` | High | `child_process.exec` — shell command execution |

---

## Built-in Skills

| Skill | Description |
|---|---|
| `builtin.security-review` | Static security checks with severity classification |
| `builtin.bug-hunt` | Runtime, logic, and edge-case defect detection |
| `builtin.filesystem` | File operations within the workspace |

---

## Requirements

- **Node.js** 18+
- **Python** 3.10+
- An OpenAI-compatible API provider (Ollama runs locally for free)

---

## Publishing (Maintainers)

```bash
npm login
npm version 0.77.0
npm publish --access public
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ENEEDAUTH` | Run `npm login` or configure your npm token |
| `E403` on publish | Your npm account needs 2FA-bypass publish permissions or OTP |
| `No working Python executable found` | Set `DYSC_PYTHON` env var to a valid Python binary path |
| Health check fails on workspace | Run `dysc workspace use-current` to reset to current directory |
| Provider key not found | Check with `dysc provider key-status <id>` and verify env var |

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install locally: `npm install -g .`
4. Test your changes: `dysc health`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

MIT — see [LICENSE](./LICENSE).

---

<div align="center">

**DYSC Agent v0.77** — Built by [Aditya Shenvi](https://github.com/aditya4232)

</div>
