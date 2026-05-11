"""
Kimari Console -- Clean terminal output rendering.

Provides functions for rendering structured human-readable output
for CLI commands. No external dependencies (no rich, etc.).
JSON output is handled separately by CLI commands -- these functions
only produce human-readable terminal text.
"""

from kimari.console.render import (
    render_doctor_table,
    render_gateway_summary,
    render_next_steps,
    render_status_table,
)

__all__ = [
    "render_doctor_table",
    "render_gateway_summary",
    "render_next_steps",
    "render_status_table",
]
