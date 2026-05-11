#!/usr/bin/env python3
"""Read-only CLI for checking Hugging Face Jobs status.

Queries HF Jobs for status and logs. Read-only — does not modify anything.

Usage:
    python training/scripts/hf_jobs_status.py --job-id <id> --json
    python training/scripts/hf_jobs_status.py --job-id <id> --logs
    python training/scripts/hf_jobs_status.py --job-id <id> --logs --tail 100
    python training/scripts/hf_jobs_status.py --job-id <id> --logs --sanitize-logs
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

# Patterns to sanitize from logs
SANITIZE_PATTERNS = [
    re.compile(r"(hf_[a-zA-Z0-9]{20,})", re.IGNORECASE),
    re.compile(r"(token[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?)", re.IGNORECASE),
    re.compile(r"(api_key[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{20,}[\"']?)", re.IGNORECASE),
    re.compile(r"(password[\s]*[=:][\s]*[\"']?[a-zA-Z0-9_\-]{8,}[\"']?)", re.IGNORECASE),
    re.compile(r"(Authorization[\s]*[:=][\s]*[\"']?Bearer[\s]+[a-zA-Z0-9_\-\.]{20,}[\"']?)", re.IGNORECASE),
]


def sanitize_line(line: str) -> str:
    """Remove sensitive patterns from a log line."""
    for pattern in SANITIZE_PATTERNS:
        line = pattern.sub("[REDACTED]", line)
    return line


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
    parser.add_argument(
        "--sanitize-logs",
        action="store_true",
        dest="sanitize_logs",
        help="Sanitize logs by removing tokens, API keys, passwords, and auth headers",
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

            # Sanitize if requested
            if args.sanitize_logs:
                tailed = [sanitize_line(line) for line in tailed]

            if args.json_output:
                print(json.dumps({
                    "job_id": args.job_id,
                    "log_lines": len(lines),
                    "showing": len(tailed),
                    "logs": "\n".join(tailed),
                    "sanitized": args.sanitize_logs,
                }, indent=2))
            else:
                sanitized_note = " (sanitized)" if args.sanitize_logs else ""
                print(f"Logs for job {args.job_id}{sanitized_note} (last {len(tailed)} of {len(lines)} lines):")
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

            # Sanitize inspect output if requested
            inspect_output = result.stdout
            if args.sanitize_logs:
                inspect_output = sanitize_line(inspect_output)

            if args.json_output:
                # Try to parse as JSON, fallback to raw text
                try:
                    data = json.loads(inspect_output)
                    data["_job_id"] = args.job_id
                    data["_read_only"] = True
                    data["_sanitized"] = args.sanitize_logs
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(json.dumps({
                        "job_id": args.job_id,
                        "raw_output": inspect_output,
                        "_read_only": True,
                        "_sanitized": args.sanitize_logs,
                    }, indent=2))
            else:
                sanitized_note = " (sanitized)" if args.sanitize_logs else ""
                print(f"Job status for: {args.job_id}{sanitized_note}")
                print("-" * 60)
                print(inspect_output)
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
