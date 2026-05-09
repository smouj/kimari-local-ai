"""
GPU profile listing and management for Kimari.
"""

import json

from kimari.utils.colors import Color


def list_profiles(config: dict, json_output: bool = False) -> dict:
    """List configured GPU profiles.

    If json_output is True, prints JSON and returns the config.
    Otherwise, prints human-readable profile list.
    """
    profiles = config.get("profiles", {})
    default = config.get("default_profile", "gtx1060")

    if json_output:
        print(json.dumps(config, indent=2))
        return config

    print(f"\n  {Color.BOLD}GPU Profiles{Color.RESET}\n")
    for key, profile in profiles.items():
        is_default = key == default
        marker = f" {Color.GREEN}(default){Color.RESET}" if is_default else ""
        print(f"  {Color.CYAN}{key}{Color.RESET}{marker}")
        print(f"    Name:    {profile['name']}")
        print(f"    Model:   {profile['model']}")
        print(f"    Host:    {profile.get('host', '127.0.0.1')}:{profile.get('port', 11435)}")
        print(f"    Ctx:     {profile.get('ctx', 'N/A'):>6}")
        print(f"    Batch:   {profile.get('batch', 'N/A'):>6}")
        print(f"    UBatch:  {profile.get('ubatch', 'N/A'):>6}")
        print(f"    Quant:   {profile['quantization']}")
        print(f"    VRAM:    {profile.get('vram_total_gb', 'N/A')} GB")
        print(f"    Cache K: {profile.get('cache_type_k', 'f16')}")
        print(f"    Cache V: {profile.get('cache_type_v', 'f16')}")
        if profile.get("notes"):
            print(f"    Notes:   {profile['notes']}")
        print()

    return config
