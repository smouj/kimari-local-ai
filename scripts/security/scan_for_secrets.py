#!/usr/bin/env python3
"""Scan files and directories for potential secrets and sensitive patterns.

Searches for patterns like HF tokens, API keys, passwords, private keys,
and sensitive paths that should not be committed to a repository.

Allows documented false positives in example/template files when marked
with inline markers like '# safe-example' or '// safe-placeholder'.

Usage:
    python scripts/security/scan_for_secrets.py --paths README.md docs training
    python scripts/security/scan_for_secrets.py --paths README.md docs training eval tests --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Patterns that indicate potential secrets or sensitive data
# Each entry: (pattern, name, severity)
SECRET_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"hf_[a-zA-Z0-9]{30,}", re.IGNORECASE), "HF token (hf_...)", "critical"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE), "OpenAI-style API key (sk-...)", "critical"),
    (re.compile(r"api_key\s*=\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "API key assignment", "high"),
    (re.compile(r"password\s*=\s*['\"][^'\"]{4,}['\"]", re.IGNORECASE), "Password assignment", "high"),
    (re.compile(r"token\s*=\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE), "Token assignment", "high"),
    (re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"), "Private key (PEM)", "critical"),
    (re.compile(r"AWS_ACCESS_KEY_ID\s*=\s*['\"][A-Z0-9]{16,}['\"]", re.IGNORECASE), "AWS access key", "critical"),
    (
        re.compile(r"Authorization:\s*Bearer\s+[a-zA-Z0-9._-]{10,}", re.IGNORECASE),
        "Bearer token in header",
        "high",
    ),
]

# Sensitive path patterns
SENSITIVE_PATH_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (
        re.compile(r"/home/[a-z][a-z0-9_]*/", re.IGNORECASE),
        "Linux home path with real username",
        "medium",
    ),
    (
        re.compile(r"/Users/[a-z][a-z0-9_]*/", re.IGNORECASE),
        "macOS home path with real username",
        "medium",
    ),
    (
        re.compile(r"C:\\Users\\[a-z][a-z0-9_]*\\", re.IGNORECASE),
        "Windows user path with real username",
        "medium",
    ),
]

# Generic usernames that are safe placeholders
SAFE_USERNAMES = {
    "user",
    "username",
    "admin",
    "test",
    "example",
    "placeholder",
    "your_user",
    "youruser",
    "name",
}

# Inline markers that indicate a false positive is documented
SAFE_MARKERS = [
    "# safe-example",
    "// safe-placeholder",
    "# safe-placeholder",
    "# placeholder",
    "// placeholder",
    "# example-only",
    "// example-only",
    "<!-- safe-example -->",
    "<!-- placeholder -->",
]

# File extensions to skip
SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".mp4",
    ".mp3",
    ".wav",
    ".ogg",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".dylib",
    ".exe",
    ".bin",
    ".safetensors",
    ".gguf",
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".db",
    ".sqlite",
    ".lock",
}

# Directories to always skip
SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".tox",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".venv",
    "venv",
    "env",
}

# Files that are themselves security guides discussing token patterns
# These files intentionally contain example token patterns for educational purposes
SECURITY_GUIDE_FILES = {
    "HF_TOKEN_SAFETY.md",
    "SECURITY.md",
    "PRIVACY.md",
    "REVERSE_PROXY_AUTH.md",
    "PRIVATE_EVAL_RESULTS_POLICY.md",
}


def _is_safe_username_in_path(path_str: str, match_str: str) -> bool:
    """Check if a matched path contains a safe placeholder username."""
    for pattern, _, _ in SENSITIVE_PATH_PATTERNS:
        m = pattern.search(match_str)
        if m:
            parts = m.group().strip("/\\").split("/")
            if len(parts) >= 2:
                username = parts[1].lower()
                if username in SAFE_USERNAMES:
                    return True
    return False


def _line_has_safe_marker(line: str) -> bool:
    """Check if a line has an inline marker indicating a documented false positive."""
    lower = line.lower()
    return any(marker.lower() in lower for marker in SAFE_MARKERS)


def _should_skip_file(path: Path) -> bool:
    """Check if a file should be skipped based on extension or directory."""
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    for part in path.parts:
        if part in SKIP_DIRS or part.endswith(".egg-info"):
            return True
    # Skip security guide files that intentionally discuss token patterns
    return path.name in SECURITY_GUIDE_FILES


def scan_file(path: Path) -> list[dict]:
    """Scan a single file for potential secrets.

    Returns a list of findings, each with:
    - file: str — path relative to project root
    - line: int — line number (1-indexed)
    - pattern: str — name of the detected pattern
    - severity: str — critical, high, or medium
    - content: str — the matched content (truncated)
    """
    findings: list[dict] = []

    if _should_skip_file(path):
        return findings

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    rel_path = str(path.relative_to(PROJECT_ROOT)) if path.is_relative_to(PROJECT_ROOT) else str(path)

    lines = text.splitlines()
    for line_num, line in enumerate(lines, start=1):
        if _line_has_safe_marker(line):
            continue

        for pattern, name, severity in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                lower_line = line.lower().strip()
                if any(
                    marker in lower_line
                    for marker in [
                        "your-api-key",
                        "your_api_key",
                        "replace_with",
                        "<your",
                        "example.com",
                        "sk-...",
                        "hf_...",
                    ]
                ):
                    continue

                findings.append(
                    {
                        "file": rel_path,
                        "line": line_num,
                        "pattern": name,
                        "severity": severity,
                        "content": match.group()[:80],
                    }
                )

        for pattern, name, severity in SENSITIVE_PATH_PATTERNS:
            match = pattern.search(line)
            if match:
                if _is_safe_username_in_path(line, match.group()):
                    continue
                findings.append(
                    {
                        "file": rel_path,
                        "line": line_num,
                        "pattern": name,
                        "severity": severity,
                        "content": match.group()[:80],
                    }
                )

    return findings


def scan_paths(paths: list[Path]) -> list[dict]:
    """Scan multiple paths (files and directories) for secrets."""
    all_findings: list[dict] = []
    seen_files: set[Path] = set()

    for p in paths:
        if p.is_file():
            if p not in seen_files:
                seen_files.add(p)
                all_findings.extend(scan_file(p))
        elif p.is_dir():
            for fp in sorted(p.rglob("*")):
                if fp.is_file() and fp not in seen_files:
                    seen_files.add(fp)
                    all_findings.extend(scan_file(fp))

    return all_findings


def main() -> None:
    """CLI entry point for the secret scanner."""
    parser = argparse.ArgumentParser(
        description="Scan files and directories for potential secrets. No external dependencies required.",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        required=True,
        help="Paths to scan (files or directories, relative to project root)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON",
    )
    args = parser.parse_args()

    resolved_paths: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.exists():
            resolved_paths.append(path)
        else:
            print(f"WARNING: Path does not exist: {path}", file=sys.stderr)

    findings = scan_paths(resolved_paths)

    if args.json_output:
        output = {
            "scanner": "scan_for_secrets.py",
            "version": "1.0.0",
            "paths_scanned": [str(p) for p in resolved_paths],
            "total_findings": len(findings),
            "critical": len([f for f in findings if f["severity"] == "critical"]),
            "high": len([f for f in findings if f["severity"] == "high"]),
            "medium": len([f for f in findings if f["severity"] == "medium"]),
            "findings": findings,
        }
        print(json.dumps(output, indent=2))
    else:
        if not findings:
            print("✅ No secrets detected in scanned paths.")
        else:
            print(f"⚠️  Found {len(findings)} potential secret(s):\n")
            for f in findings:
                severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(f["severity"], "⚪")
                print(f"  {severity_icon} [{f['severity'].upper()}] {f['file']}:{f['line']}")
                print(f"     Pattern: {f['pattern']}")
                print(f"     Content: {f['content']}")
                print()

        critical_count = len([f for f in findings if f["severity"] == "critical"])
        if critical_count > 0:
            print(
                f"❌ {critical_count} critical finding(s) detected — review before committing.",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
