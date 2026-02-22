#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');

const runtimePath = path.resolve(__dirname, '..', 'agent-runtime', 'main.py');

function resolvePythonExecutable() {
  const candidates = [];
  if (process.env.DYSC_PYTHON && process.env.DYSC_PYTHON.trim().length > 0) {
    candidates.push(process.env.DYSC_PYTHON.trim());
  }
  if (process.platform === 'win32') {
    candidates.push('C:/Users/Aditya/AppData/Local/Microsoft/WindowsApps/python3.13.exe');
  }
  candidates.push('python3', 'python', 'py');

  for (const candidate of candidates) {
    const probe = spawnSync(candidate, ['--version'], { encoding: 'utf-8' });
    if (!probe.error && probe.status === 0) {
      return candidate;
    }
  }
  return null;
}

function printUsage() {
  console.log(`
DYSC CLI

Usage:
  dysc init
  dysc start
  dysc health

  node apps/cli/main.js init
  node apps/cli/main.js start
  node apps/cli/main.js health
  node apps/cli/main.js doctor
  node apps/cli/main.js context packages
  node apps/cli/main.js review security [--limit <n>]
  node apps/cli/main.js fix suggest --file <path> --line <n> --rule <id> --snippet <text>

  node apps/cli/main.js provider list
  node apps/cli/main.js provider add --id <id> --type <openai_compatible|provider_specific> --base-url <url> --api-key-env <ENV> [--enabled true|false]
  node apps/cli/main.js provider set-primary <id>

  node apps/cli/main.js workspace show
  node apps/cli/main.js workspace set <path>

  node apps/cli/main.js skills list
  node apps/cli/main.js skills enable <skillId>
  node apps/cli/main.js skills disable <skillId>
  node apps/cli/main.js skills install-local <skillId> <jsonPath>

  node apps/cli/main.js chat save --session <id> --role <user|assistant|system> --content <text>
  node apps/cli/main.js chat list <sessionId>
`);
}

function parseFlags(args) {
  const flags = {};
  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    if (!token.startsWith('--')) {
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
    console.error('No working Python executable found. Set DYSC_PYTHON to your Python path.');
    process.exit(1);
  }

  const args = pythonExecutable === 'py'
    ? ['-3', runtimePath, ...runtimeArgs]
    : [runtimePath, ...runtimeArgs];

  const result = spawnSync(pythonExecutable, args, {
    stdio: 'inherit',
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

if (command === 'init' || command === 'start' || command === 'health' || command === 'doctor') {
  runRuntime([command, ...remaining]);
}

if (command === 'provider') {
  dispatchSubcommand(subcommand, {
    list: () => runRuntime(['provider-list']),
    'set-primary': () => runRuntime(['provider-set-primary', rest[0] || '']),
    add: () => {
      const flags = parseFlags(rest);
      runRuntime([
        'provider-add',
        flags.id || '',
        flags.type || '',
        flags['base-url'] || '',
        flags['api-key-env'] || '',
        flags.enabled || 'true',
      ]);
    },
  });
}

if (command === 'workspace') {
  dispatchSubcommand(subcommand, {
    show: () => runRuntime(['workspace-show']),
    set: () => runRuntime(['workspace-set', rest[0] || '']),
  });
}

if (command === 'skills') {
  dispatchSubcommand(subcommand, {
    list: () => runRuntime(['skills-list']),
    enable: () => runRuntime(['skills-enable', rest[0] || '']),
    disable: () => runRuntime(['skills-disable', rest[0] || '']),
    'install-local': () => runRuntime(['skills-install-local', rest[0] || '', rest[1] || '']),
  });
}

if (command === 'chat') {
  dispatchSubcommand(subcommand, {
    list: () => runRuntime(['chat-list', rest[0] || '']),
    save: () => {
      const flags = parseFlags(rest);
      runRuntime([
        'chat-save',
        flags.session || '',
        flags.role || '',
        flags.content || '',
      ]);
    },
  });
}

if (command === 'context') {
  dispatchSubcommand(subcommand, {
    packages: () => runRuntime(['context-packages']),
  });
}

if (command === 'review') {
  dispatchSubcommand(subcommand, {
    security: () => {
      const flags = parseFlags(rest);
      runRuntime(['review-security', flags.limit || '150']);
    },
  });
}

if (command === 'fix') {
  dispatchSubcommand(subcommand, {
    suggest: () => {
      const flags = parseFlags(rest);
      runRuntime([
        'fix-suggest',
        flags.file || '',
        flags.line || '',
        flags.rule || '',
        flags.snippet || '',
      ]);
    },
  });
}

printUsage();
process.exit(1);
