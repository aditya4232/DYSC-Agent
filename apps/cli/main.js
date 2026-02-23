#!/usr/bin/env node

const { spawnSync } = require("child_process");
const path = require("path");

const runtimePath = path.resolve(__dirname, "..", "agent-runtime", "main.py");

const DYSC_VERSION = "0.77.0";

function resolvePythonExecutable() {
  const candidates = [];
  if (process.env.DYSC_PYTHON && process.env.DYSC_PYTHON.trim().length > 0) {
    candidates.push(process.env.DYSC_PYTHON.trim());
  }
  candidates.push("python3", "python", "py");

  for (const candidate of candidates) {
    const probe = spawnSync(candidate, ["--version"], { encoding: "utf-8" });
    if (!probe.error && probe.status === 0) {
      return candidate;
    }
  }
  return null;
}

function printUsage() {
  console.log(`
DYSC Agent v${DYSC_VERSION}
Security-first coding CLI agent

Usage:
  dysc init                          Initialize config and directories
  dysc onboard [workspacePath]       First-time guided setup
  dysc start                         Launch interactive AI agent
  dysc start --once                  Run readiness check and exit
  dysc health                        System health check
  dysc doctor                        Alias for health

  dysc provider list                 List configured providers
  dysc provider add --id <id> --type <type> --base-url <url> --api-key-env <ENV> [--enabled true|false]
  dysc provider set-primary <id>     Set primary provider
  dysc provider set-key-env <id> <ENV>
  dysc provider key-status <id>      Check API key presence

  dysc workspace show                Show workspace config
  dysc workspace set <path>          Set primary workspace
  dysc workspace open <path>         Open a local project
  dysc workspace use-current         Use current directory

  dysc settings show                 Show current settings
  dysc settings set <key> <value>    Update a setting

  dysc context packages              Snapshot runtime dependencies

  dysc review security [--limit <n>] Run security scan
  dysc fix suggest --file <path> --line <n> --rule <id> --snippet <text>

  dysc skills list                   List all skills
  dysc skills enable <skillId>       Enable a skill
  dysc skills disable <skillId>      Disable a skill
  dysc skills install-local <skillId> <jsonPath>

  dysc chat save --session <id> --role <role> --content <text>
  dysc chat list <sessionId>

  dysc --version                     Show version

Environment:
  DYSC_PYTHON    Path to Python executable (auto-detected if unset)
`);
}

function parseFlags(args) {
  const flags = {};
  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    if (!token.startsWith("--")) {
      continue;
    }
    const key = token.slice(2);
    const value = args[i + 1];
    flags[key] = value;
    i += 1;
  }
  return flags;
}

function runRuntime(runtimeArgs) {
  const pythonExecutable = resolvePythonExecutable();
  if (!pythonExecutable) {
    console.error(
      "No working Python executable found. Set DYSC_PYTHON to your Python path.",
    );
    process.exit(1);
  }

  const args =
    pythonExecutable === "py"
      ? ["-3", runtimePath, ...runtimeArgs]
      : [runtimePath, ...runtimeArgs];

  const result = spawnSync(pythonExecutable, args, {
    stdio: "inherit",
  });

  if (result.error) {
    console.error(`Runtime invocation failed: ${result.error.message}`);
    process.exit(1);
  }
  process.exit(result.status ?? 1);
}

function dispatchSubcommand(subcommand, handlers) {
  const handler = handlers[subcommand];
  if (!handler) {
    printUsage();
    process.exit(1);
  }
  handler();
}

const args = process.argv.slice(2);
if (args.length === 0) {
  printUsage();
  process.exit(0);
}

const command = args[0];
const remaining = args.slice(1);
const subcommand = remaining[0];
const rest = remaining.slice(1);

if (command === "--version" || command === "-v") {
  console.log(`dysc-agent v${DYSC_VERSION}`);
  process.exit(0);
}

if (
  command === "init" ||
  command === "start" ||
  command === "health" ||
  command === "doctor" ||
  command === "onboard"
) {
  runRuntime([command, ...remaining]);
}

if (command === "provider") {
  dispatchSubcommand(subcommand, {
    list: () => runRuntime(["provider-list"]),
    "set-primary": () => runRuntime(["provider-set-primary", rest[0] || ""]),
    "set-key-env": () =>
      runRuntime(["provider-set-key-env", rest[0] || "", rest[1] || ""]),
    "key-status": () => runRuntime(["provider-key-status", rest[0] || ""]),
    add: () => {
      const flags = parseFlags(rest);
      runRuntime([
        "provider-add",
        flags.id || "",
        flags.type || "",
        flags["base-url"] || "",
        flags["api-key-env"] || "",
        flags.enabled || "true",
      ]);
    },
  });
}

if (command === "settings") {
  dispatchSubcommand(subcommand, {
    show: () => runRuntime(["settings-show"]),
    set: () => runRuntime(["settings-set", rest[0] || "", rest[1] || ""]),
  });
}

if (command === "workspace") {
  dispatchSubcommand(subcommand, {
    show: () => runRuntime(["workspace-show"]),
    set: () => runRuntime(["workspace-set", rest[0] || ""]),
    open: () => runRuntime(["workspace-open", rest[0] || ""]),
    "use-current": () => runRuntime(["workspace-use-current"]),
  });
}

if (command === "skills") {
  dispatchSubcommand(subcommand, {
    list: () => runRuntime(["skills-list"]),
    enable: () => runRuntime(["skills-enable", rest[0] || ""]),
    disable: () => runRuntime(["skills-disable", rest[0] || ""]),
    "install-local": () =>
      runRuntime(["skills-install-local", rest[0] || "", rest[1] || ""]),
  });
}

if (command === "chat") {
  dispatchSubcommand(subcommand, {
    list: () => runRuntime(["chat-list", rest[0] || ""]),
    save: () => {
      const flags = parseFlags(rest);
      runRuntime([
        "chat-save",
        flags.session || "",
        flags.role || "",
        flags.content || "",
      ]);
    },
  });
}

if (command === "context") {
  dispatchSubcommand(subcommand, {
    packages: () => runRuntime(["context-packages"]),
  });
}

if (command === "review") {
  dispatchSubcommand(subcommand, {
    security: () => {
      const flags = parseFlags(rest);
      runRuntime(["review-security", flags.limit || "150"]);
    },
  });
}

if (command === "fix") {
  dispatchSubcommand(subcommand, {
    suggest: () => {
      const flags = parseFlags(rest);
      runRuntime([
        "fix-suggest",
        flags.file || "",
        flags.line || "",
        flags.rule || "",
        flags.snippet || "",
      ]);
    },
  });
}

printUsage();
process.exit(1);
