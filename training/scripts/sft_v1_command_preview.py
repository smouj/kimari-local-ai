#!/usr/bin/env python3
"""Generate safe command previews for Kimari Runtime 1.5B SFT v1.

The script only prints commands and metadata. It never executes training or HF
Jobs operations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, raw_value = stripped.partition(":")
        value = raw_value.strip().strip('"').strip("'")
        lowered = value.lower()
        if lowered == "true":
            parsed: Any = True
        elif lowered == "false":
            parsed = False
        elif lowered in {"null", "~"}:
            parsed = None
        else:
            try:
                parsed = int(value)
            except ValueError:
                try:
                    parsed = float(value)
                except ValueError:
                    parsed = value
        data[key.strip()] = parsed
    return data


def shell_join(args: list[str]) -> str:
    quoted: list[str] = []
    for arg in args:
        if not arg or any(char.isspace() or char in "'\"$`\\" for char in arg):
            quoted.append("'" + arg.replace("'", "'\\''") + "'")
        else:
            quoted.append(arg)
    return " ".join(quoted)


def build_preview(config: dict[str, Any], config_path: Path) -> dict[str, Any]:
    run_id = str(config.get("run_id", "kimari-runtime-15b-sft-v1"))
    local_dry_run_args = [
        "python",
        "training/scripts/train_sft_lora.py",
        "--config",
        str(config_path),
        "--dry-run",
    ]
    hf_dry_run_args = [
        "python",
        "training/scripts/hf_jobs_sft_v1.py",
        "--config",
        str(config_path),
        "--dry-run",
        "--print-command",
    ]
    blocked_real_args = [
        "python",
        "training/scripts/hf_jobs_sft_v1.py",
        "--config",
        str(config_path),
        "--allow-submit",
        "--yes",
    ]
    return {
        "run_id": run_id,
        "base_model": config.get("base_model"),
        "gate_state": config.get("gate_state"),
        "commands": {
            "local_dry_run": shell_join(local_dry_run_args),
            "hf_jobs_dry_run": shell_join(hf_dry_run_args),
            "blocked_real_command": shell_join(blocked_real_args),
        },
        "expected_variables": [
            "HF_TOKEN in environment for future HF Jobs access checks only; never pass tokens as CLI args",
            "Optional HF_HOME/cache variables if the future training runner needs custom cache paths",
            "No WANDB_API_KEY because report_to=none",
        ],
        "expected_artifacts": [
            str(config.get("output_dir", "training/runs/kimari-runtime-15b-sft-v1")),
            "Private local LoRA/QLoRA adapter files only after a future approved real run",
            "Run summary JSON based on training/templates/sft_v1_run_summary.template.json",
        ],
        "forbidden_artifacts": [
            "Public adapter repository",
            "Committed adapter weights (*.safetensors, *.bin, *.pt, checkpoints)",
            "GGUF files",
            "Raw logs containing tokens, secrets, PII, or private prompts",
            "Public benchmark claims before eval and manual review",
        ],
        "estimated_cost": "$0.50-2.00 for 100 steps on A10G via HF Jobs",
        "security_warnings": [
            "Preview only: no command is executed by this script.",
            "Real HF Jobs submission is blocked in v0.1.60-alpha.",
            "push_to_hub=false, hf_public_upload_allowed=false, gguf_export_allowed=false must remain enforced.",
            "Gate remains BLOCKED until eval plus manual review explicitly transition it.",
        ],
    }


def to_markdown(preview: dict[str, Any]) -> str:
    lines = [
        f"# SFT v1 Command Preview — {preview['run_id']}",
        "",
        f"- Base model: `{preview['base_model']}`",
        f"- Gate: `{preview['gate_state']}`",
        f"- Estimated cost: {preview['estimated_cost']}",
        "",
        "## Commands",
    ]
    for name, command in preview["commands"].items():
        lines.extend(["", f"### {name}", "```bash", command, "```"])
    for section in ("expected_variables", "expected_artifacts", "forbidden_artifacts", "security_warnings"):
        title = section.replace("_", " ").title()
        lines.extend(["", f"## {title}"])
        lines.extend(f"- {item}" for item in preview[section])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Print SFT v1 command previews without executing them.")
    parser.add_argument("--config", type=Path, required=True, help="Path to SFT v1 YAML config")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown")
    args = parser.parse_args()

    config = parse_simple_yaml(args.config)
    preview = build_preview(config, args.config)
    if args.markdown:
        print(to_markdown(preview), end="")
    elif args.json_output:
        print(json.dumps(preview, indent=2, sort_keys=True))
    else:
        print(to_markdown(preview), end="")


if __name__ == "__main__":
    main()
