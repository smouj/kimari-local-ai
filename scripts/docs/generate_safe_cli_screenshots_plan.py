#!/usr/bin/env python3
"""Generate a PLAN for capturing CLI screenshots.

This script does NOT generate images. It outputs a structured plan
listing which CLI commands should be captured, with safety notes
and metadata. The plan can be output as JSON or Markdown.

Usage:
    python scripts/docs/generate_safe_cli_screenshots_plan.py
    python scripts/docs/generate_safe_cli_screenshots_plan.py --json
    python scripts/docs/generate_safe_cli_screenshots_plan.py --markdown
    python scripts/docs/generate_safe_cli_screenshots_plan.py --output plan.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _get_kimari_version() -> str:
    """Read __version__ from kimari/__init__.py without importing the package."""
    init_path = PROJECT_ROOT / "kimari" / "__init__.py"
    if not init_path.exists():
        return "unknown"
    for line in init_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            # e.g. __version__ = "0.1.27-alpha"
            return line.split('"')[1]
    return "unknown"


KIMARI_VERSION = _get_kimari_version()


# ---------------------------------------------------------------------------
# Screenshot plans — each entry describes a CLI command to capture
# ---------------------------------------------------------------------------

SCREENSHOT_PLANS: list[dict[str, str]] = [
    {
        "command": "kimari status",
        "description": "Server status — running state, profile, model, host, port, uptime",
        "category": "status",
        "safety_notes": "No tokens. No API keys. Shows only local paths and model names.",
        "status": "planned",
    },
    {
        "command": "kimari doctor --deep",
        "description": "Extended diagnostics — 14 checks with PASS/WARN/FAIL table",
        "category": "diagnostics",
        "safety_notes": "No tokens. No real benchmarks. Shows environment info only.",
        "status": "planned",
    },
    {
        "command": "kimari gateway --plan",
        "description": "Gateway endpoint plan — shows planned endpoints and security constraints",
        "category": "gateway",
        "safety_notes": "No tokens. No real server. Plan-only output.",
        "status": "planned",
    },
    {
        "command": "kimari integrations generate --all",
        "description": "Generate integration config snippets for all supported targets",
        "category": "integrations",
        "safety_notes": "No tokens. No API keys. No auto-writing. Output to stdout only.",
        "status": "planned",
    },
    {
        "command": "kimari benchmark --dry-run",
        "description": "Benchmark dry-run plan — shows what would be measured without executing",
        "category": "benchmark",
        "safety_notes": "No real benchmarks. No model execution. Plan-only output.",
        "status": "planned",
    },
    {
        "command": "kimari update check",
        "description": "Update check — current version, latest available, recommended action",
        "category": "update",
        "safety_notes": "No tokens. No auto-update. Offline by default.",
        "status": "planned",
    },
]


# ---------------------------------------------------------------------------
# Output generators
# ---------------------------------------------------------------------------


def _generate_json() -> str:
    """Return the plan as structured JSON."""
    payload: dict[str, Any] = {
        "kimari_version": KIMARI_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_plans": len(SCREENSHOT_PLANS),
        "plans": SCREENSHOT_PLANS,
    }
    return json.dumps(payload, indent=2)


def _generate_markdown() -> str:
    """Return the plan as a Markdown table."""
    lines = [
        f"# CLI Screenshot Plan — Kimari v{KIMARI_VERSION}",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Total plans: {len(SCREENSHOT_PLANS)}",
        "",
        "| # | Command | Description | Category | Safety Notes | Status |",
        "|---|---------|-------------|----------|-------------|--------|",
    ]
    for i, plan in enumerate(SCREENSHOT_PLANS, 1):
        lines.append(
            f"| {i} | `{plan['command']}` | {plan['description']} "
            f"| {plan['category']} | {plan['safety_notes']} | {plan['status']} |"
        )
    lines.append("")
    lines.append("## Safety Guidelines")
    lines.append("")
    lines.append("- No tokens or API keys in any capture")
    lines.append("- No real benchmark results (dry-run only)")
    lines.append("- No private paths (use generic `/home/user/` in examples)")
    lines.append("- No unreviewed content — all captures must be reviewed before commit")
    lines.append("")
    return "\n".join(lines)


def _generate_default() -> str:
    """Return the plan as plain text (default output)."""
    lines = [
        f"CLI Screenshot Plan — Kimari v{KIMARI_VERSION}",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Total plans: {len(SCREENSHOT_PLANS)}",
        "",
    ]
    for i, plan in enumerate(SCREENSHOT_PLANS, 1):
        lines.append(f"  [{i}] {plan['command']}")
        lines.append(f"      Description:  {plan['description']}")
        lines.append(f"      Category:     {plan['category']}")
        lines.append(f"      Safety:       {plan['safety_notes']}")
        lines.append(f"      Status:       {plan['status']}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a PLAN for capturing CLI screenshots. Does NOT generate images — only a structured plan.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON with plan entries and metadata.",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output as Markdown table.",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.json_output:
        output = _generate_json()
    elif args.markdown:
        output = _generate_markdown()
    else:
        output = _generate_default()

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")


if __name__ == "__main__":
    main()
