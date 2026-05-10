#!/usr/bin/env python3
"""Select base model for Kimari-4B fine-tuning.

Reads base_candidates.yaml and calculates heuristic scoring.
No network calls. No model downloads.

Usage:
    python training/scripts/select_base_model.py [--config PATH] [--json]
        [--prefer-license-open] [--prefer-coding] [--prefer-spanish]
        [--target-vram GB]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Default scoring per criterion (1-5) for each candidate
DEFAULT_SCORES: dict[str, dict[str, int]] = {
    "smollm3-3b": {
        "license_clarity": 5,
        "redistribution_compatibility": 5,
        "tokenizer_stability": 3,
        "gguf_support": 3,
        "coding_ability": 3,
        "spanish_technical": 2,
        "agent_json": 3,
        "inference_viability": 4,
        "training_cost": 4,
    },
    "qwen2.5-3b-instruct": {
        "license_clarity": 3,
        "redistribution_compatibility": 3,
        "tokenizer_stability": 4,
        "gguf_support": 4,
        "coding_ability": 5,
        "spanish_technical": 4,
        "agent_json": 4,
        "inference_viability": 4,
        "training_cost": 4,
    },
    "llama-3.2-3b-instruct": {
        "license_clarity": 2,
        "redistribution_compatibility": 2,
        "tokenizer_stability": 5,
        "gguf_support": 5,
        "coding_ability": 4,
        "spanish_technical": 3,
        "agent_json": 4,
        "inference_viability": 4,
        "training_cost": 3,
    },
}

DEFAULT_CRITERIA: dict[str, int] = {
    "license_clarity": 3,
    "redistribution_compatibility": 3,
    "tokenizer_stability": 2,
    "gguf_support": 2,
    "coding_ability": 2,
    "spanish_technical": 1,
    "agent_json": 2,
    "inference_viability": 2,
    "training_cost": 1,
}


def parse_simple_yaml(path: Path) -> dict | None:
    """Parse base_candidates.yaml with a simple fallback parser.

    No PyYAML dependency required. This handles the specific structure
    of base_candidates.yaml. Returns None if parsing fails.
    """
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        pass

    # Simple fallback parser for our specific YAML structure
    text = path.read_text()
    candidates = []
    current_candidate: dict | None = None
    criteria: dict[str, dict] = {}
    in_criteria = False
    current_criterion_name = ""

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "candidates:":
            in_criteria = False
            continue

        if stripped == "scoring_criteria:":
            in_criteria = True
            if current_candidate is not None:
                candidates.append(current_candidate)
                current_candidate = None
            continue

        if in_criteria:
            # Parse criteria entries like "license_clarity:\n  weight: 3\n  description: ..."
            if line.startswith("  ") and not line.startswith("    "):
                # Criterion name line (2-space indent, not 4)
                candidate_key = stripped.rstrip(":")
                if (
                    candidate_key
                    and not candidate_key.startswith("weight")
                    and not candidate_key.startswith("description")
                ):
                    current_criterion_name = candidate_key
                    criteria[current_criterion_name] = {}
            elif line.startswith("    "):
                # Criterion property (4-space indent)
                if "weight:" in stripped and current_criterion_name:
                    try:
                        weight_val = int(stripped.split("weight:")[1].strip().strip('"').strip("'"))
                        criteria[current_criterion_name]["weight"] = weight_val
                    except (ValueError, IndexError):
                        pass
        else:
            # Parse candidates
            if stripped.startswith("- id:"):
                if current_candidate is not None:
                    candidates.append(current_candidate)
                current_candidate = {"id": stripped.split("id:")[1].strip().strip('"').strip("'")}
            elif current_candidate is not None and ":" in stripped:
                key, _, value = stripped.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if value:
                    # Try numeric conversion
                    try:
                        if "." in value.replace("~", ""):
                            current_candidate[key] = value  # keep as string for ~3B
                        else:
                            current_candidate[key] = int(value)
                    except ValueError:
                        current_candidate[key] = value

    if current_candidate is not None:
        candidates.append(current_candidate)

    result: dict = {"candidates": candidates, "scoring_criteria": {}}
    for name, data in criteria.items():
        if "weight" in data:
            result["scoring_criteria"][name] = data
    return result


def compute_weighted_score(
    candidate_id: str,
    scores: dict[str, int],
    criteria_weights: dict[str, int],
) -> int:
    """Compute weighted score for a candidate."""
    total = 0
    for criterion, weight in criteria_weights.items():
        total += scores.get(criterion, 0) * weight
    return total


def main() -> None:
    """CLI entry point for base model selection."""
    parser = argparse.ArgumentParser(
        description="Select base model for Kimari-4B fine-tuning. No network calls. No model downloads.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "configs" / "base_candidates.yaml",
        help="Path to base_candidates.yaml config file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--prefer-license-open",
        action="store_true",
        help="Double the weight of license clarity and redistribution compatibility",
    )
    parser.add_argument(
        "--prefer-coding",
        action="store_true",
        help="Double the weight of coding ability",
    )
    parser.add_argument(
        "--prefer-spanish",
        action="store_true",
        help="Double the weight of Spanish technical ability",
    )
    parser.add_argument(
        "--target-vram",
        type=float,
        default=None,
        help="Filter candidates by max VRAM (GB) for Q4 quantization",
    )

    args = parser.parse_args()

    # Load config
    config_path = args.config
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    data = parse_simple_yaml(config_path)
    if data is None:
        print("ERROR: Failed to parse config file", file=sys.stderr)
        sys.exit(1)

    # Extract criteria weights from config, fall back to defaults
    config_criteria = data.get("scoring_criteria", {})
    criteria_weights: dict[str, int] = {}
    for name, info in config_criteria.items():
        if isinstance(info, dict) and "weight" in info:
            criteria_weights[name] = int(info["weight"])
    if not criteria_weights:
        criteria_weights = dict(DEFAULT_CRITERIA)

    # Apply preference modifiers
    if args.prefer_license_open:
        criteria_weights["license_clarity"] = criteria_weights.get("license_clarity", 3) * 2
        criteria_weights["redistribution_compatibility"] = criteria_weights.get("redistribution_compatibility", 3) * 2
    if args.prefer_coding:
        criteria_weights["coding_ability"] = criteria_weights.get("coding_ability", 2) * 2
    if args.prefer_spanish:
        criteria_weights["spanish_technical"] = criteria_weights.get("spanish_technical", 1) * 2

    # Process candidates
    candidates = data.get("candidates", [])
    if not candidates:
        print("ERROR: No candidates found in config", file=sys.stderr)
        sys.exit(1)

    results = []
    for cand in candidates:
        cand_id = cand.get("id", "unknown")
        scores = DEFAULT_SCORES.get(cand_id, {})
        weighted = compute_weighted_score(cand_id, scores, criteria_weights)

        # Filter by VRAM if specified
        vram_q4 = cand.get("expected_vram_q4_gb", 99)
        try:
            vram_q4 = float(str(vram_q4))
        except (ValueError, TypeError):
            vram_q4 = 99.0

        if args.target_vram is not None and vram_q4 > args.target_vram:
            continue

        # Determine license annotation
        license_name = str(cand.get("license", "unknown")).lower()
        if license_name in ("apache-2.0", "mit", "cc-by-4.0", "cc0"):
            license_note = "license open — recommended if capability is sufficient"
        elif "llama" in license_name or "meta" in license_name:
            license_note = "license constraints — review required before use"
        elif "qwen" in license_name or "research" in license_name:
            license_note = "license review required — terms must be verified"
        else:
            license_note = "license status unknown"

        results.append(
            {
                "id": cand_id,
                "hf_repo": cand.get("hf_repo", ""),
                "license": cand.get("license", "unknown"),
                "license_note": license_note,
                "weighted_score": weighted,
                "ranking": cand.get("ranking", 99),
                "risk_level": cand.get("risk_level", "unknown"),
                "context_length": cand.get("context_length", 0),
                "expected_vram_q4_gb": vram_q4,
            }
        )

    # Sort by weighted score descending
    results.sort(key=lambda r: r["weighted_score"], reverse=True)

    if args.json_output:
        print(json.dumps({"ranking": results, "criteria_weights": criteria_weights}, indent=2))
        return

    # Human-readable output
    print("Kimari-4B Base Model Selection")
    print("=" * 50)
    print()
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['id']} — score: {r['weighted_score']}/90")
        print(f"     License: {r['license']} ({r['license_note']})")
        print(f"     Risk: {r['risk_level']} | Context: {r['context_length']} | VRAM Q4: {r['expected_vram_q4_gb']} GB")
        print()

    if results:
        top = results[0]
        print(f"Recommendation: {top['id']} — {top['license_note']}")
    print()
    print("No base model has been selected. All candidates are under review.")


if __name__ == "__main__":
    main()
