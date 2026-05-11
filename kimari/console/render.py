"""
Kimari Console Render -- Terminal output rendering functions.

Pure functions that return strings for human-readable CLI output.
No external dependencies. No printing -- callers decide what to do
with the returned text.
"""


def render_status_table(data: dict) -> str:
    """Render a clean key-value status table.

    Expected keys (all optional, handled gracefully):
        Version, Config, Models, Default profile, Server, Gateway,
        Benchmark, Preview gate, and any arbitrary keys.

    Returns:
        A formatted string with aligned key-value pairs.
    """
    lines: list[str] = []

    # Define preferred key order for known fields
    known_order = [
        "Version",
        "Config",
        "Models",
        "Default profile",
        "Server",
        "Host",
        "Port",
        "Gateway",
        "Benchmark",
        "Preview gate",
    ]

    # Build items in preferred order, then append any unknown keys
    items: list[tuple[str, str]] = []
    seen_keys: set[str] = set()

    for key in known_order:
        if key in data and data[key] is not None:
            items.append((key, str(data[key])))
            seen_keys.add(key)

    for key, value in data.items():
        if key not in seen_keys and value is not None:
            items.append((key, str(value)))
            seen_keys.add(key)

    if not items:
        return "  (no status data)"

    # Calculate alignment width
    max_key_len = max(len(k) for k, _ in items)

    for key, value in items:
        padding = " " * (max_key_len - len(key))
        lines.append(f"  {key}:{padding} {value}")

    return "\n".join(lines)


def render_doctor_table(checks: list[dict]) -> str:
    """Render a PASS/WARN/FAIL table from doctor --deep checks.

    Each check dict should have:
        name (str): Check name
        status (str): "ok"/"pass", "warn", or "fail"
        value (str): Check result value
        detail (str, optional): Additional detail

    Returns:
        A formatted string with status icons and a summary line.
    """
    if not checks:
        return "  (no checks to display)"

    # Status icon mapping -- Windows-safe, no emojis
    status_icons = {
        "ok": "\u2713",  # check mark
        "pass": "\u2713",  # check mark
        "warn": "\u26a0",  # warning sign
        "fail": "\u2717",  # ballot x
    }

    lines: list[str] = []
    counts = {"pass": 0, "warn": 0, "fail": 0}

    # Calculate alignment
    max_name_len = max(len(c.get("name", "")) for c in checks)

    for check in checks:
        name = check.get("name", "unknown")
        status = check.get("status", "warn").lower()
        value = check.get("value", "")
        detail = check.get("detail", "")

        icon = status_icons.get(status, "?")
        padding = " " * (max_name_len - len(name))

        line = f"  {icon} {name}:{padding} {value}"
        if detail:
            line += f"  ({detail})"

        lines.append(line)

        # Count
        if status in ("ok", "pass"):
            counts["pass"] += 1
        elif status == "warn":
            counts["warn"] += 1
        elif status == "fail":
            counts["fail"] += 1

    # Summary line
    total = sum(counts.values())
    summary_parts = [f"{counts['pass']} passed"]
    if counts["warn"] > 0:
        summary_parts.append(f"{counts['warn']} warnings")
    if counts["fail"] > 0:
        summary_parts.append(f"{counts['fail']} failed")

    lines.append("")
    lines.append(f"  Summary: {', '.join(summary_parts)} ({total} checks)")

    return "\n".join(lines)


def render_gateway_summary(plan_or_status: dict) -> str:
    """Render gateway plan/status summary.

    Shows planned endpoints count, security constraints, host/port.

    Returns:
        A formatted string with gateway details.
    """
    lines: list[str] = []

    lines.append("  Gateway Summary:")

    endpoints = plan_or_status.get("endpoints", plan_or_status.get("planned_endpoints"))
    if endpoints is not None:
        if isinstance(endpoints, list):
            lines.append(f"    Endpoints:      {len(endpoints)} planned")
        else:
            lines.append(f"    Endpoints:      {endpoints}")

    security = plan_or_status.get("security_constraints", plan_or_status.get("security"))
    if security is not None:
        if isinstance(security, list):
            lines.append(f"    Security:       {len(security)} constraints")
        else:
            lines.append(f"    Security:       {security}")

    host = plan_or_status.get("host")
    if host:
        lines.append(f"    Host:           {host}")

    port = plan_or_status.get("port")
    if port:
        lines.append(f"    Port:           {port}")

    status = plan_or_status.get("status")
    if status:
        lines.append(f"    Status:         {status}")

    # Handle any additional keys
    known_keys = {
        "endpoints",
        "planned_endpoints",
        "security_constraints",
        "security",
        "host",
        "port",
        "status",
    }
    for key, value in plan_or_status.items():
        if key not in known_keys and value is not None:
            lines.append(f"    {key}: {value}")

    if len(lines) <= 1:
        lines.append("    (no gateway data available)")

    return "\n".join(lines)


def render_next_steps(items: list[str]) -> str:
    """Render a "Next steps" section with numbered items.

    Returns:
        A formatted string with numbered next steps.
    """
    if not items:
        return "  Next steps: (none)"

    lines: list[str] = ["  Next steps:"]
    for i, item in enumerate(items, 1):
        lines.append(f"    {i}. {item}")

    return "\n".join(lines)
