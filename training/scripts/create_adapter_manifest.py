#!/usr/bin/env python3
"""Create an adapter manifest from a template and training artifacts.

Reads the template from training/templates/adapter_manifest.template.yaml,
fills in values from the run config and adapter directory, and writes the
result to the specified output path.

If the adapter directory exists and --dry-run is not set, computes sizes
and SHA-256 hashes of allowed files. Suspicious files (.safetensors, .bin,
.pt, .pth, .ckpt, .gguf) are listed but their content is NOT included.

preview_gate_state is always BLOCKED.
public_release_allowed is always false.
hf_upload_allowed is always false.

Works with or without PyYAML (simple text substitution fallback).

No model downloads. No HF uploads. No weights committed.

Usage:
    python training/scripts/create_adapter_manifest.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --adapter-dir training/adapters/kimari-smollm3-sft-v0 \\
        --output MANIFEST.yaml
    python training/scripts/create_adapter_manifest.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --adapter-dir training/adapters/kimari-smollm3-sft-v0 \\
        --dry-run
    python training/scripts/create_adapter_manifest.py \\
        --run-config training/configs/private_sft_run.v0.yaml \\
        --output MANIFEST.json \\
        --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# File extensions that are suspicious — listed but NOT included in manifest
SUSPICIOUS_EXTENSIONS = {".safetensors", ".bin", ".pt", ".pth", ".ckpt", ".gguf"}

# Default paths relative to repo root
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "adapter_manifest.template.yaml"
DEFAULT_RUN_CONFIG = Path(__file__).resolve().parent.parent / "configs" / "private_sft_run.v0.yaml"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_simple_yaml(path: Path) -> dict:
    """Parse a simple YAML file. Uses PyYAML if available, else fallback.

    The fallback handles key: value pairs (strings, numbers, booleans,
    null/empty) and simple lists. It does NOT handle nested dicts deeply.
    """
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass

    text = path.read_text(encoding="utf-8")
    result: dict = {}
    current_list_key: str | None = None
    current_list: list = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List item
        if stripped.startswith("- ") and current_list_key is not None:
            item = stripped[2:].strip().strip('"').strip("'")
            current_list.append(item)
            continue

        # Flush previous list
        if current_list_key is not None:
            result[current_list_key] = current_list
            current_list_key = None
            current_list = []

        # Key-value pair
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if not value:
                # Could be start of a nested structure or null
                current_list_key = key
                current_list = []
                continue

            # Strip quotes
            value = value.strip('"').strip("'")

            # Boolean conversion
            if value.lower() == "true":
                result[key] = True
            elif value.lower() == "false":
                result[key] = False
            elif value.lower() in ("null", "~", "none"):
                result[key] = None
            else:
                # Try numeric conversion
                try:
                    result[key] = int(value)
                except ValueError:
                    try:
                        result[key] = float(value)
                    except ValueError:
                        result[key] = value

    # Flush last list
    if current_list_key is not None:
        result[current_list_key] = current_list

    return result


def render_yaml_from_dict(data: dict) -> str:
    """Render a dict to YAML string. Uses PyYAML if available, else fallback."""
    try:
        import yaml

        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    except ImportError:
        pass

    lines: list[str] = []
    _render_yaml_lines(data, lines, indent=0)
    return "\n".join(lines) + "\n"


def _render_yaml_lines(data: object, lines: list[str], indent: int) -> None:
    """Recursively render data to YAML lines (simple fallback)."""
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    # List of dicts
                    lines.append(f"{prefix}{key}:")
                    for item in value:
                        lines.append(f"{prefix}  - ")
                        first = True
                        for k, v in item.items():
                            if first:
                                lines[-1] += f"{k}: {_yaml_scalar(v)}"
                                first = False
                            else:
                                lines.append(f"{prefix}    {k}: {_yaml_scalar(v)}")
                elif isinstance(value, list):
                    lines.append(f"{prefix}{key}:")
                    for item in value:
                        lines.append(f"{prefix}  - {_yaml_scalar(item)}")
                else:
                    lines.append(f"{prefix}{key}:")
                    _render_yaml_lines(value, lines, indent + 1)
            else:
                lines.append(f"{prefix}{key}: {_yaml_scalar(value)}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{prefix}- ")
                first = True
                for k, v in item.items():
                    if first:
                        lines[-1] += f"{k}: {_yaml_scalar(v)}"
                        first = False
                    else:
                        lines.append(f"{prefix}  {k}: {_yaml_scalar(v)}")
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")


def _yaml_scalar(value: object) -> str:
    """Format a scalar value for YAML output."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    # Quote strings that could be ambiguous
    if any(
        c in s for c in (":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`")
    ):
        return f'"{s}"'
    if not s:
        return '""'
    return s


def scan_adapter_dir(adapter_dir: Path) -> tuple[list[dict], list[str], int, str]:
    """Scan adapter directory for allowed files.

    Returns:
        (adapter_files, suspicious_files, total_size_bytes, combined_sha256)
        adapter_files: list of {name, size_bytes, sha256} for allowed files
        suspicious_files: list of filenames that were rejected
        total_size_bytes: total size of allowed files
        combined_sha256: SHA-256 of concatenated allowed file hashes
    """
    adapter_files: list[dict] = []
    suspicious_files: list[str] = []
    total_size = 0
    hash_parts: list[str] = []

    if not adapter_dir.exists():
        return adapter_files, suspicious_files, total_size, ""

    for child in sorted(adapter_dir.rglob("*")):
        if not child.is_file():
            continue

        # Skip checkpoint subdirectories
        if any("checkpoint-" in part for part in child.parts):
            continue

        # Skip runs/ subdirectories (TensorBoard)
        if any(part == "runs" for part in child.parts):
            continue

        rel_name = str(child.relative_to(adapter_dir))

        # Check suspicious extensions
        if child.suffix.lower() in SUSPICIOUS_EXTENSIONS:
            suspicious_files.append(rel_name)
            continue

        # Compute hash and size for allowed files
        try:
            file_hash = sha256_file(child)
            file_size = child.stat().st_size
            total_size += file_size
            hash_parts.append(f"{rel_name}:{file_hash}")
            adapter_files.append(
                {
                    "name": rel_name,
                    "size_bytes": file_size,
                    "sha256": file_hash,
                }
            )
        except OSError as exc:
            print(f"WARNING: Could not read {child}: {exc}", file=sys.stderr)

    # Combined hash of all allowed file hashes
    combined = hashlib.sha256("|".join(hash_parts).encode()).hexdigest() if hash_parts else ""

    return adapter_files, suspicious_files, total_size, combined


def build_manifest(
    template_path: Path,
    run_config_path: Path,
    adapter_dir: Path | None,
    now_iso: str | None = None,
) -> dict:
    """Build a manifest dict from template, run config, and adapter directory.

    preview_gate_state is always BLOCKED.
    public_release_allowed is always false.
    hf_upload_allowed is always false.
    """
    if now_iso is None:
        now_iso = datetime.now(timezone.utc).isoformat()

    # Load template
    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    manifest = parse_simple_yaml(template_path)

    # Load run config and merge relevant fields
    if run_config_path.exists():
        run_config = parse_simple_yaml(run_config_path)
        if "run_id" in run_config and run_config["run_id"]:
            manifest["run_id"] = run_config["run_id"]
        if "base_model" in run_config and run_config["base_model"]:
            manifest["base_model"] = run_config["base_model"]
        if "sft_config" in run_config and run_config["sft_config"]:
            manifest["training_config"] = run_config["sft_config"]
        if "output_dir" in run_config and run_config["output_dir"]:
            # Infer adapter_name from output_dir
            manifest["adapter_name"] = Path(run_config["output_dir"]).name

    # Load SFT config for hyperparameters
    training_config_path = Path(str(manifest.get("training_config", "")))
    if training_config_path.exists():
        sft_config = parse_simple_yaml(training_config_path)
        for key in ("lora_r", "lora_alpha", "lora_dropout", "learning_rate", "max_seq_length"):
            if key in sft_config:
                manifest[key] = sft_config[key]
        if "num_train_epochs" in sft_config:
            manifest["epochs"] = sft_config["num_train_epochs"]

    # Scan adapter directory if provided
    if adapter_dir is not None and adapter_dir.exists():
        adapter_files, suspicious, total_size, combined_hash = scan_adapter_dir(adapter_dir)
        manifest["adapter_files"] = adapter_files
        manifest["adapter_size_bytes"] = total_size
        manifest["adapter_sha256"] = combined_hash

        if suspicious:
            print(f"WARNING: Suspicious files found in {adapter_dir} (listed but NOT included):", file=sys.stderr)
            for sf in suspicious:
                print(f"  - {sf}", file=sys.stderr)

    # Enforce safety constraints — these MUST always be these values
    manifest["preview_gate_state"] = "BLOCKED"
    manifest["public_release_allowed"] = False
    manifest["hf_upload_allowed"] = False

    # Ensure state_history has initial BLOCKED entry
    if not manifest.get("state_history"):
        manifest["state_history"] = [
            {
                "state": "BLOCKED",
                "date": now_iso,
                "actor": "create_adapter_manifest.py",
                "reason": "Initial state after manifest creation",
            }
        ]

    return manifest


def main() -> None:
    """CLI entry point for creating adapter manifests."""
    parser = argparse.ArgumentParser(
        description="Create an adapter manifest from template and training artifacts. "
        "No model downloads. No HF uploads. No weights committed.",
    )
    parser.add_argument(
        "--run-config",
        type=Path,
        default=DEFAULT_RUN_CONFIG,
        help="Path to training run config YAML (default: training/configs/private_sft_run.v0.yaml)",
    )
    parser.add_argument(
        "--adapter-dir",
        type=Path,
        default=None,
        help="Path to adapter directory (e.g., training/adapters/kimari-smollm3-sft-v0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("MANIFEST.yaml"),
        help="Output path for manifest (default: MANIFEST.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write file, just print what would be created",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON instead of YAML",
    )

    args = parser.parse_args()

    # Build manifest
    manifest = build_manifest(
        template_path=DEFAULT_TEMPLATE,
        run_config_path=args.run_config,
        adapter_dir=args.adapter_dir,
    )

    # Format output
    if args.json_output:
        output_text = json.dumps(manifest, indent=2, default=str) + "\n"
    else:
        # Add header comment
        header = (
            "# Adapter Manifest — Kimari Local AI\n"
            f"# Generated: {manifest.get('state_history', [{}])[0].get('date', 'unknown')}\n"
            "# preview_gate_state: BLOCKED (no automatic transitions)\n"
            "# public_release_allowed: false\n"
            "# hf_upload_allowed: false\n"
            "# See docs/ADAPTER_PREVIEW_GATE.md for state transitions.\n\n"
        )
        output_text = header + render_yaml_from_dict(manifest)

    # Output
    if args.dry_run:
        print(output_text)
    else:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
        print(f"Manifest written to: {output_path}", file=sys.stderr)
        # Also print to stdout for verification
        print(output_text)


if __name__ == "__main__":
    main()
