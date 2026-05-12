#!/usr/bin/env python3
"""Create a sanitized adapter manifest from training output.

Reads the output directory, computes hashes, and generates a manifest
that is safe to commit (no private paths, no tokens, no raw logs).

Usage:
    python training/scripts/create_kimari4b_adapter_manifest.py --output-dir training/adapters/kimari4b-private-adapter-v0 --config training/configs/kimari4b_private_adapter_run.v0.yaml
    python training/scripts/create_kimari4b_adapter_manifest.py --output-dir training/adapters/kimari4b-private-adapter-v0 --config ... --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

TEMPLATE_PATH = PROJECT_ROOT / "training" / "templates" / "kimari4b_adapter_manifest.template.json"

# Patterns that must NEVER appear in manifest
FORBIDDEN_PATTERNS = [
    "/home/",
    "sk-",
    "hf_",
    "api_key",
    "token",
    "password",
    "secret",
]


def compute_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """Compute hash of a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def sanitize_path(path_str: str) -> str:
    """Remove private path components."""
    # Only keep relative path from project root
    abs_path = Path(path_str).resolve()
    try:
        return str(abs_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return Path(path_str).name


def check_forbidden(content: str) -> list[str]:
    """Check content for forbidden patterns."""
    found = []
    lower = content.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in lower:
            found.append(pattern)
    return found


def create_manifest(output_dir: str, config_path: str) -> dict:
    """Create adapter manifest from output dir and config."""
    # Load template
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Template not found: {TEMPLATE_PATH}")
        sys.exit(1)

    manifest = json.loads(TEMPLATE_PATH.read_text())

    # Load config
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required")
        sys.exit(1)
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Fill from config
    manifest["run_id"] = config.get("run_id", "")
    manifest["base_model"] = config.get("base_model", {}).get("name", "")
    manifest["base_model_license"] = config.get("base_model", {}).get("license", "")
    manifest["dataset_name"] = config.get("dataset", {}).get("name", "")
    manifest["dataset_hash"] = config.get("dataset", {}).get("hash", "")
    manifest["dataset_examples"] = config.get("dataset", {}).get("estimated_examples", 0)
    manifest["lora_r"] = config.get("lora", {}).get("r", 0)
    manifest["lora_alpha"] = config.get("lora", {}).get("lora_alpha", 0)
    manifest["learning_rate"] = str(config.get("training", {}).get("learning_rate", ""))
    manifest["epochs"] = config.get("training", {}).get("num_train_epochs", 0)

    # Safety flags from config
    safety = config.get("safety", {})
    manifest["public_release_allowed"] = safety.get("public_release_allowed", False)
    manifest["hf_upload_allowed"] = safety.get("hf_upload_allowed", False)
    manifest["gguf_generated"] = safety.get("gguf_export_allowed", False)
    manifest["push_to_hub"] = safety.get("push_to_hub", False)
    manifest["gate_state"] = safety.get("preview_gate_state", "BLOCKED")
    manifest["auto_gate_transition"] = config.get("auto_gate_transition", False)
    manifest["manual_review_required"] = config.get("manual_review_required", True)

    # Try to read from output dir
    output_path = Path(output_dir)
    if output_path.exists():
        # Find safetensors files
        safetensors = list(output_path.glob("*.safetensors"))
        if safetensors:
            total_size = sum(f.stat().st_size for f in safetensors)
            manifest["adapter_size_bytes"] = total_size
            manifest["adapter_size_human"] = f"{total_size / (1024**2):.1f} MB"
            # Hash the adapter files (combined hash)
            combined_hash = hashlib.sha256()
            for f in sorted(safetensors):
                combined_hash.update(compute_file_hash(f).encode())
            manifest["adapter_hash"] = combined_hash.hexdigest()[:16]

        # Try to find trainer_state.json for training info
        trainer_state = output_path / "trainer_state.json"
        if trainer_state.exists():
            try:
                state = json.loads(trainer_state.read_text())
                log_history = state.get("log_history", [])
                if log_history:
                    manifest["final_loss"] = log_history[-1].get("loss", 0)
            except (json.JSONDecodeError, KeyError):
                pass

    manifest["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Verify no forbidden patterns
    manifest_str = json.dumps(manifest, indent=2)
    forbidden = check_forbidden(manifest_str)
    if forbidden:
        print(f"ERROR: Manifest contains forbidden patterns: {forbidden}")
        sys.exit(1)

    # NEVER advance gate automatically
    if manifest["gate_state"] not in ("BLOCKED", "PRIVATE_ADAPTER_READY", "EVAL_PENDING", "REVIEW_PENDING"):
        manifest["gate_state"] = "BLOCKED"
        print("WARNING: Gate state was not BLOCKED/standard. Reset to BLOCKED.")

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Kimari-4B adapter manifest")
    parser.add_argument("--output-dir", required=True, help="Path to adapter output directory")
    parser.add_argument("--config", required=True, help="Path to config YAML")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    manifest = create_manifest(args.output_dir, args.config)

    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print("Kimari-4B Adapter Manifest")
        print("=" * 50)
        for key, value in manifest.items():
            print(f"  {key}: {value}")
        print("=" * 50)
        print(f"  Gate: {manifest['gate_state']}")
        print(f"  Public release: {manifest['public_release_allowed']}")
        print(f"  HF upload: {manifest['hf_upload_allowed']}")


if __name__ == "__main__":
    main()
