#!/usr/bin/env python3
"""Read-only CLI for checking Hugging Face Jobs status.

Queries HF Jobs for status and logs. Read-only — does not modify anything.

Usage:
    python training/scripts/hf_jobs_status.py --job-id <id> --json
    python training/scripts/hf_jobs_status.py --job-id <id> --logs
    python training/scripts/hf_jobs_status.py --job-id <id> --logs --tail 100
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check Hugging Face Jobs status (read-only). "
        "Does not modify or cancel any jobs. No tokens accepted as arguments."
    )
    parser.add_argument(
        "--job-id",
        required=True,
        help="HF Jobs job ID to inspect",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output structured JSON result",
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Show job logs",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=100,
        help="Number of log lines to show (default: 100, used with --logs)",
    )

    args = parser.parse_args()

    if args.logs:
        # Get logs
        try:
            result = subprocess.run(
                ["hf", "jobs", "logs", args.job_id],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print(f"ERROR: Failed to get logs: {result.stderr}", file=sys.stderr)
                sys.exit(1)

            lines = result.stdout.splitlines()
            tailed = lines[-args.tail:] if len(lines) > args.tail else lines

            if args.json_output:
                print(json.dumps({
                    "job_id": args.job_id,
                    "log_lines": len(lines),
                    "showing": len(tailed),
                    "logs": "\n".join(tailed),
                }, indent=2))
            else:
                print(f"Logs for job {args.job_id} (last {len(tailed)} of {len(lines)} lines):")
                print("-" * 60)
                for line in tailed:
                    print(line)
        except FileNotFoundError:
            print("ERROR: 'hf' CLI not found", file=sys.stderr)
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print("ERROR: Log retrieval timed out", file=sys.stderr)
            sys.exit(1)
    else:
        # Get job info
        try:
            result = subprocess.run(
                ["hf", "jobs", "inspect", args.job_id],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"ERROR: Failed to inspect job: {result.stderr}", file=sys.stderr)
                sys.exit(1)

            if args.json_output:
                # Try to parse as JSON, fallback to raw text
                try:
                    data = json.loads(result.stdout)
                    data["_job_id"] = args.job_id
                    data["_read_only"] = True
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(json.dumps({
                        "job_id": args.job_id,
                        "raw_output": result.stdout,
                        "_read_only": True,
                    }, indent=2))
            else:
                print(f"Job status for: {args.job_id}")
                print("-" * 60)
                print(result.stdout)
                print("-" * 60)
                print("(Read-only — no modifications made)")
        except FileNotFoundError:
            print("ERROR: 'hf' CLI not found", file=sys.stderr)
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print("ERROR: Job inspection timed out", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
