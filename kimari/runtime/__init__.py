"""
Kimari runtime module.

Provides utilities for detecting and validating llama-server capabilities
at runtime, including supported flags and version information.
"""

from kimari.runtime.llama_flags import (
    detect_llama_server_help,
    detect_llama_server_version,
    filter_unsupported_flags,
    parse_supported_flags,
    supports_flag,
)

__all__ = [
    "detect_llama_server_help",
    "detect_llama_server_version",
    "parse_supported_flags",
    "supports_flag",
    "filter_unsupported_flags",
]
