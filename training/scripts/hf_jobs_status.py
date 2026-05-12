#!/usr/bin/env python3
"""Check HF Jobs status and retrieve sanitized logs.

Usage:
    python training/scripts/hf_jobs_status.py --job-id <ID> --inspect --json
    python training/scripts/hf_jobs_status.py --job-id <ID> --logs --sanitize-logs --tail 120
"""

from __future__ import annotations

import argparse
import json
import subprocess


def get_job_status(job_id: str) -> dict:
    """Get job status via HF CLI."""
    try:
        result = subprocess.run(
            ["hf", "jobs", "status", job_id],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "job_id": job_id,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"job_id": job_id, "error": "Command timed out"}
    except Exception as e:
        return {"job_id": job_id, "error": str(e)}


def get_job_logs(job_id: str, sanitize: bool = True, tail: int = 120) -> dict:
    """Get job logs via HF CLI, optionally sanitized."""
    try:
        result = subprocess.run(
            ["hf", "jobs", "logs", job_id],
            capture_output=True,
            text=True,
            timeout=30,
        )
        logs = result.stdout.strip()

        if sanitize:
            # Remove any lines that might contain tokens or private data
            forbidden_patterns = [
                "hf_",
                "sk-",
                "api_key",
                "token",
                "password",
                "secret",
                "/home/",
                "credential",
            ]
            lines = logs.split("\n")
            sanitized = []
            for line in lines:
                lower = line.lower()
                skip = False
                for pattern in forbidden_patterns:
                    if pattern in lower and pattern != "token" and pattern != "secret":
                        # Keep lines that just mention "token" in context like "gate_state: BLOCKED"
                        skip = True
                        break
                if not skip:
                    sanitized.append(line)
            logs = "\n".join(sanitized[-tail:]) if len(sanitized) > tail else "\n".join(sanitized)
        else:
            logs = "\n".join(logs.split("\n")[-tail:])

        return {"job_id": job_id, "logs": logs, "sanitized": sanitize}
    except subprocess.TimeoutExpired:
        return {"job_id": job_id, "error": "Command timed out"}
    except Exception as e:
        return {"job_id": job_id, "error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Check HF Jobs status")
    parser.add_argument("--job-id", required=True, help="Job ID to inspect")
    parser.add_argument("--inspect", action="store_true", help="Get job status")
    parser.add_argument("--logs", action="store_true", help="Get job logs")
    parser.add_argument("--sanitize-logs", action="store_true", help="Sanitize logs (remove private data)")
    parser.add_argument("--tail", type=int, default=120, help="Number of log lines to keep")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = {}

    if args.inspect:
        result["status"] = get_job_status(args.job_id)

    if args.logs:
        result["logs"] = get_job_logs(args.job_id, sanitize=args.sanitize_logs, tail=args.tail)

    if not args.inspect and not args.logs:
        # Default: inspect
        result["status"] = get_job_status(args.job_id)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"\n{'=' * 50}")
            print(f"{key.upper()}")
            print(f"{'=' * 50}")
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"  {value}")


if __name__ == "__main__":
    main()
