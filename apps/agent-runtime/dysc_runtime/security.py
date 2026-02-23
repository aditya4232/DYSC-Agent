import re
from pathlib import Path

from .workspace import get_effective_workspace


SECURITY_RULES = [
    {
        "id": "PY-EVAL-001",
        "severity": "high",
        "pattern": re.compile(r"\beval\s*\("),
        "message": "Use of eval can lead to arbitrary code execution.",
        "fix": "Replace eval with safe parsing/dispatch logic.",
    },
    {
        "id": "PY-EXEC-001",
        "severity": "high",
        "pattern": re.compile(r"\bexec\s*\("),
        "message": "Use of exec can execute untrusted code.",
        "fix": "Use explicit function mapping instead of dynamic execution.",
    },
    {
        "id": "PY-SHELL-001",
        "severity": "high",
        "pattern": re.compile(r"shell\s*=\s*True"),
        "message": "shell=True may allow command injection.",
        "fix": "Pass argument arrays and keep shell=False.",
    },
    {
        "id": "PY-REQUESTS-001",
        "severity": "medium",
        "pattern": re.compile(r"verify\s*=\s*False"),
        "message": "TLS certificate verification disabled.",
        "fix": "Keep TLS verification enabled in production.",
    },
    {
        "id": "PY-HASH-001",
        "severity": "medium",
        "pattern": re.compile(r"hashlib\.(md5|sha1)\s*\("),
        "message": "Weak hash algorithm detected.",
        "fix": "Prefer SHA-256+ or password hashing (bcrypt/argon2).",
    },
    {
        "id": "JS-EVAL-001",
        "severity": "high",
        "pattern": re.compile(r"\beval\s*\("),
        "message": "JavaScript eval is unsafe with untrusted input.",
        "fix": "Use structured parsing and explicit handlers.",
    },
    {
        "id": "JS-FUNCTION-001",
        "severity": "high",
        "pattern": re.compile(r"new\s+Function\s*\("),
        "message": "Dynamic function construction is unsafe.",
        "fix": "Use static functions and controlled dispatch.",
    },
    {
        "id": "JS-EXEC-001",
        "severity": "high",
        "pattern": re.compile(r"child_process\.(exec|execSync)\s*\("),
        "message": "Shell command execution is high risk.",
        "fix": "Use spawn/spawnSync with validated args.",
    },
]


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
}


def _workspace_root():
    workspace = get_effective_workspace()
    return Path(workspace).resolve() if workspace else Path.cwd().resolve()


def _language_for_path(path):
    extension = path.suffix.lower()
    if extension in {".py"}:
        return "python"
    if extension in {".js", ".ts", ".jsx", ".tsx"}:
        return "javascript"
    return "other"


def _should_scan(path):
    return path.suffix.lower() in {".py", ".js", ".ts", ".jsx", ".tsx"}


def run_security_review(limit=150):
    root = _workspace_root()
    findings = []
    scanned_files = 0

    for file_path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in file_path.parts):
            continue
        if not file_path.is_file() or not _should_scan(file_path):
            continue

        scanned_files += 1
        if scanned_files > 1200:
            break

        language = _language_for_path(file_path)

        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#") or stripped.startswith("\"") or stripped.startswith("'"):
                continue

            for rule in SECURITY_RULES:
                if language == "python" and not rule["id"].startswith("PY-"):
                    continue
                if language == "javascript" and not rule["id"].startswith("JS-"):
                    continue
                if language == "other":
                    continue

                if rule["pattern"].search(line):
                    findings.append(
                        {
                            "id": f"{rule['id']}:{len(findings) + 1}",
                            "rule": rule["id"],
                            "severity": rule["severity"],
                            "file": str(file_path.relative_to(root)).replace("\\", "/"),
                            "line": line_number,
                            "message": rule["message"],
                            "snippet": line.strip(),
                            "suggested_fix": rule["fix"],
                        }
                    )
                    if len(findings) >= limit:
                        break
            if len(findings) >= limit:
                break
        if len(findings) >= limit:
            break

    severity_rank = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda item: (severity_rank.get(item["severity"], 9), item["file"], item["line"]))

    return {
        "ok": True,
        "workspace": str(root),
        "scanned_files": scanned_files,
        "findings_count": len(findings),
        "findings": findings,
    }


def suggest_human_fix(file_path, line, rule, snippet):
    return {
        "ok": True,
        "strategy": "human-robust",
        "target": {"file": file_path, "line": line, "rule": rule},
        "analysis": f"Risky code detected near line {line}: {snippet}",
        "patch_plan": [
            "Replace dynamic execution with explicit, validated code paths.",
            "Add input validation and constrained allow-lists before sensitive operations.",
            "Add error handling for failure paths and security-relevant edge cases.",
            "Add regression test covering the vulnerable and fixed behavior.",
        ],
    }
