#!/usr/bin/env python3
"""GGUF export plan for Kimari fine-tuned models.

Prints expected commands for GGUF conversion and quantization.
Does NOT convert if llama.cpp tools are not available.
Validates no GGUF files are uploaded to the repo.

No network calls. No model downloads.

Usage:
    python training/scripts/export_gguf_plan.py --model-dir PATH --output-dir PATH
        [--quant Q4_K_M,Q5_K_M,IQ4_XS] [--dry-run]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_llamacpp_tools() -> dict[str, str | None]:
    """Find llama.cpp conversion and quantization tools."""
    tools = {"convert_hf_to_gguf": None, "llama_quantize": None}

    # Check common locations
    candidates = [
        Path.home() / "llama.cpp",
        Path("/usr/local/src/llama.cpp"),
        Path("/opt/llama.cpp"),
    ]

    # Also check if tools are on PATH
    if shutil.which("convert_hf_to_gguf.py"):
        tools["convert_hf_to_gguf"] = shutil.which("convert_hf_to_gguf.py")
    if shutil.which("llama-quantize"):
        tools["llama_quantize"] = shutil.which("llama-quantize")

    # Check candidate directories
    for base in candidates:
        if not base.exists():
            continue
        convert_script = base / "convert_hf_to_gguf.py"
        if convert_script.exists() and tools["convert_hf_to_gguf"] is None:
            tools["convert_hf_to_gguf"] = str(convert_script)
        quantize_bin = base / "build" / "bin" / "llama-quantize"
        if quantize_bin.exists() and tools["llama_quantize"] is None:
            tools["llama_quantize"] = str(quantize_bin)
        # Also check llama-quantize in bin/
        quantize_bin2 = base / "bin" / "llama-quantize"
        if quantize_bin2.exists() and tools["llama_quantize"] is None:
            tools["llama_quantize"] = str(quantize_bin2)

    return tools


def check_gguf_in_repo(project_root: Path) -> list[str]:
    """Check that no GGUF files are tracked in git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.gguf"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        return [f for f in result.stdout.strip().splitlines() if f]
    except Exception:
        return []


def main() -> None:
    """CLI entry point for GGUF export planning."""
    parser = argparse.ArgumentParser(
        description="GGUF export plan for Kimari fine-tuned models. "
        "Prints expected commands. Does NOT convert without llama.cpp tools. "
        "No network calls. No model downloads.",
    )
    parser.add_argument(
        "--model-dir", type=Path, required=True, help="Directory containing the fine-tuned model (safetensors)"
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for GGUF output files")
    parser.add_argument(
        "--quant",
        type=str,
        default="Q4_K_M,Q5_K_M,IQ4_XS",
        help="Comma-separated quantization types (default: Q4_K_M,Q5_K_M,IQ4_XS)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing any commands")

    args = parser.parse_args()

    quant_types = [q.strip() for q in args.quant.split(",") if q.strip()]

    print("Kimari GGUF Export Plan")
    print("=" * 40)

    # Find tools
    tools = find_llamacpp_tools()
    print(f"\nconvert_hf_to_gguf.py: {tools['convert_hf_to_gguf'] or 'NOT FOUND'}")
    print(f"llama-quantize: {tools['llama_quantize'] or 'NOT FOUND'}")

    # Check model dir
    if args.model_dir.exists():
        safetensors = list(args.model_dir.glob("*.safetensors"))
        print(f"\nModel directory: {args.model_dir}")
        print(f"Safetensors files: {len(safetensors)}")
    else:
        print(f"\nModel directory: {args.model_dir} (NOT FOUND)")

    print(f"\nOutput directory: {args.output_dir}")
    print(f"Quantization types: {', '.join(quant_types)}")

    # Print expected commands
    print("\n--- Expected Commands ---")
    print()

    convert_cmd = (
        f"python {tools['convert_hf_to_gguf'] or 'convert_hf_to_gguf.py'} "
        f"{args.model_dir} --outfile {args.output_dir / 'model-f16.gguf'} --outtype f16"
    )
    print(f"1. Convert to F16 GGUF:\n   {convert_cmd}\n")

    for qt in quant_types:
        quant_cmd = (
            f"{tools['llama_quantize'] or 'llama-quantize'} "
            f"{args.output_dir / 'model-f16.gguf'} "
            f"{args.output_dir / f'model-{qt.lower()}.gguf'} {qt}"
        )
        print(f"2. Quantize to {qt}:\n   {quant_cmd}\n")

    # Check for GGUF in repo
    project_root = Path(__file__).resolve().parent.parent.parent
    gguf_tracked = check_gguf_in_repo(project_root)
    if gguf_tracked:
        print(f"\n  WARNING: GGUF files tracked in git: {gguf_tracked}", file=sys.stderr)
        print("  GGUF files must NOT be committed to the repository.", file=sys.stderr)
    else:
        print("\n  [OK] No GGUF files tracked in git")

    # Dry-run check
    if args.dry_run:
        print("\n--- Dry-Run Mode ---")
        print("No conversion or quantization commands were executed.")
        print("To perform actual conversion:")
        print("  1. Install llama.cpp with CUDA support")
        print("  2. Ensure the fine-tuned model exists in the model directory")
        print("  3. Run without --dry-run")
        print("  4. Hash and pin the resulting GGUF files")
        print("  5. DO NOT commit GGUF files to the repository")

    # Validate tools availability
    if not tools["convert_hf_to_gguf"] or not tools["llama_quantize"]:
        print("\n  NOTE: Some llama.cpp tools not found. Install llama.cpp to proceed.", file=sys.stderr)
        if not args.dry_run:
            print("  Use --dry-run to see the planned commands without executing.", file=sys.stderr)
            sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
