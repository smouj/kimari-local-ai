#!/usr/bin/env python3
"""Check that a private LoRA adapter loads correctly on top of its base model.

This validates adapter integrity and compatibility — NOT quality or benchmarks.

Usage:
    # Check from local directory
    python training/scripts/check_private_adapter_load.py --base-model Qwen/Qwen2.5-1.5B-Instruct --adapter-dir /tmp/adapter --json

    # Check from HF private repo
    python training/scripts/check_private_adapter_load.py --base-model Qwen/Qwen2.5-1.5B-Instruct --adapter-repo Smouj013/kimari4b-micro-sft-adapter-v0 --json
"""

from __future__ import annotations

import argparse
import json
import sys


def check_adapter_load(base_model: str, adapter_dir: str | None = None, adapter_repo: str | None = None) -> dict:
    """Load base model + adapter and run a minimal generation check."""
    result = {
        "adapter_load_success": False,
        "generation_success": False,
        "error_sanitized": None,
    }

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        result["error_sanitized"] = "transformers/torch not available"
        return result

    try:
        print(f"Loading base model: {base_model}")
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16, device_map="auto")
    except Exception as e:
        result["error_sanitized"] = f"Base model load error: {type(e).__name__}"
        return result

    try:
        if adapter_repo:
            print(f"Loading adapter from HF repo: {adapter_repo}")
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, adapter_repo)
        elif adapter_dir:
            print(f"Loading adapter from local dir: {adapter_dir}")
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, adapter_dir)
        else:
            result["error_sanitized"] = "No adapter source specified"
            return result

        result["adapter_load_success"] = True
        print("Adapter loaded successfully!")
    except Exception as e:
        result["error_sanitized"] = f"Adapter load error: {type(e).__name__}"
        return result

    try:
        test_prompt = "User: ¿Qué es Kimari?\nAssistant:"
        inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=20, do_sample=False)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Test generation: {response[:80]}...")
        result["generation_success"] = True
    except Exception as e:
        result["error_sanitized"] = f"Generation error: {type(e).__name__}"

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Check private adapter load")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-1.5B-Instruct", help="Base model name")
    parser.add_argument("--adapter-dir", help="Local adapter directory")
    parser.add_argument("--adapter-repo", help="HF private adapter repo ID")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not args.adapter_dir and not args.adapter_repo:
        print("ERROR: Specify --adapter-dir or --adapter-repo", file=sys.stderr)
        sys.exit(1)

    result = check_adapter_load(args.base_model, args.adapter_dir, args.adapter_repo)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"  {k}: {v}")

    sys.exit(0 if result["adapter_load_success"] else 1)


if __name__ == "__main__":
    main()
