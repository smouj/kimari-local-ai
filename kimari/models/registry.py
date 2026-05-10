"""
Model registry management for Kimari.

Handles loading the model registry, listing models, downloading GGUF files,
and validating model integrity via SHA256 hashes.
"""

import hashlib
import json
import time
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None  # type: ignore

from kimari.core.constants import PROJECT_ROOT
from kimari.core.paths import (
    get_defaults_dir,
    get_user_models_dir,
    get_user_models_registry_path,
)
from kimari.utils.colors import Color, info, ok, warn


def _resolve_model_target(target_path: str) -> Path:
    """Resolve a model target_path to an actual filesystem path.

    Checks in order:
    1. User models directory (``~/.local/share/kimari/models/`` or equivalent)
    2. Repo-root ``models/`` (editable installs)
    """
    user_path = get_user_models_dir() / Path(target_path).name
    if user_path.exists():
        return user_path

    repo_path = PROJECT_ROOT / target_path
    if repo_path.exists():
        return repo_path

    # Default: return user path (even if it doesn't exist yet)
    return user_path


def _resolve_models_registry_path() -> Path:
    """Resolve the models registry path.

    Order:
    1. User config directory
    2. Repo-root config/ (editable installs)
    3. Packaged defaults (kimari/defaults/)
    """
    user_path = get_user_models_registry_path()
    if user_path.exists():
        return user_path

    repo_path = PROJECT_ROOT / "config" / "kimari.models.json"
    if repo_path.exists():
        return repo_path

    defaults_path = Path(get_defaults_dir()) / "kimari.models.json"
    if defaults_path.exists():
        return defaults_path

    return user_path


def load_models_registry() -> dict:
    """Load the models registry.

    Resolution order:
    1. User config directory
    2. Repo-root config/kimari.models.json
    3. Packaged defaults (kimari/defaults/kimari.models.json)
    """
    registry_path = _resolve_models_registry_path()
    if not registry_path.exists():
        print("[ERROR] Models registry not found. Searched:")
        print(f"  User config: {get_user_models_registry_path()}")
        print(f"  Repo root:   {PROJECT_ROOT / 'config' / 'kimari.models.json'}")
        print(f"  Defaults:    {Path(get_defaults_dir()) / 'kimari.models.json'}")
        raise SystemExit(1)
    with open(registry_path) as f:
        return json.load(f)


def list_registry_models(
    json_output: bool = False,
    downloaded_only: bool = False,
    status_filter: str | None = None,
) -> list:
    """List all models in the registry with download status.

    Args:
        json_output: If True, return structured data.
        downloaded_only: If True, only list models present in models/.
        status_filter: Filter by status field (e.g. 'recommended', 'test', 'experimental').

    Returns list of model entries.
    """
    registry = load_models_registry()
    models = registry.get("models", [])

    result = []
    for m in models:
        target = _resolve_model_target(m["target_path"])
        m_copy = dict(m)
        m_copy["downloaded"] = target.exists()

        if downloaded_only and not m_copy["downloaded"]:
            continue
        if status_filter and m_copy.get("status") != status_filter:
            continue

        result.append(m_copy)

    if json_output:
        return result

    # Human-readable output
    if not result:
        if downloaded_only:
            print("\n  No downloaded models found.")
        elif status_filter:
            print(f"\n  No models with status '{status_filter}' found.")
        else:
            print("\n  No models in registry.")
        return result

    print(f"\n  {Color.BOLD}Available Models for Download{Color.RESET}\n")
    for m in result:
        target = _resolve_model_target(m["target_path"])
        is_downloaded = target.exists()
        status_str = (
            f"{Color.GREEN}✓ downloaded{Color.RESET}" if is_downloaded else f"{Color.DIM}not downloaded{Color.RESET}"
        )
        status_badge = ""
        if m.get("status"):
            status_badge = f" [{m['status']}]"
        print(f"  {Color.CYAN}{m['id']:<20}{Color.RESET} {m['display_name']}{status_badge}")
        print(f"  {'':20} Size: {m['size_gb']} GB | Profile: {m.get('recommended_profile', 'N/A')} | {status_str}")
        if m.get("family"):
            print(f"  {'':20} Family: {m['family']} | Quant: {m.get('quantization', 'N/A')}")
        if m.get("sha256") and is_downloaded:
            print(f"  {'':20} SHA256: defined (verify with 'kimari models --verify')")
        print()

    return result


def _compute_sha256(filepath: Path, progress: bool = False) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    file_size = filepath.stat().st_size
    bytes_processed = 0

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
            bytes_processed += len(chunk)
            if progress and file_size > 0:
                pct = bytes_processed / file_size * 100
                print(f"\r  Verifying: {pct:5.1f}%", end="", flush=True)

    if progress:
        print()  # New line after progress
    return sha256.hexdigest()


def verify_model_hash(model_id: str) -> bool | None:
    """Verify a downloaded model's SHA256 hash against the registry.

    Returns True if match, False if mismatch, None if no hash in registry.
    """
    registry = load_models_registry()
    model_entry = None
    for m in registry.get("models", []):
        if m["id"] == model_id:
            model_entry = m
            break

    if not model_entry:
        print(f"[ERROR] Model '{model_id}' not found in registry.")
        raise SystemExit(1)

    expected_hash = model_entry.get("sha256")
    if not expected_hash:
        warn(f"No SHA256 hash defined for model '{model_id}'.")
        return None

    target = _resolve_model_target(model_entry["target_path"])
    if not target.exists():
        print(f"[ERROR] Model file not found: {target}")
        raise SystemExit(1)

    actual_hash = _compute_sha256(target, progress=True)
    if actual_hash == expected_hash:
        ok(f"SHA256 hash verified for {model_id}")
        return True
    else:
        print(f"  {Color.RED}[FAIL]{Color.RESET} SHA256 mismatch!")
        print(f"  Expected: {expected_hash}")
        print(f"  Actual:   {actual_hash}")
        return False


def pull_model(model_id: str, dry_run: bool = False, force: bool = False):
    """Download a model from the registry.

    Args:
        model_id: The model ID from the registry.
        dry_run: If True, show what would be downloaded without downloading.
        force: If True, redownload even if the file already exists.
    """
    if requests is None:
        print("[ERROR] 'requests' is required. Install with: pip install -r cli/requirements.txt")
        raise SystemExit(1)

    registry = load_models_registry()
    models = registry.get("models", [])

    # Find model by id
    model_entry = None
    for m in models:
        if m["id"] == model_id:
            model_entry = m
            break

    if not model_entry:
        print(f"[ERROR] Model '{model_id}' not found in registry.")
        available = ", ".join(m["id"] for m in models)
        print(f"  Available: {available}")
        print(f"  Use {Color.CYAN}kimari pull --list{Color.RESET} to see all models.")
        raise SystemExit(1)

    url = model_entry["url"]
    filename = model_entry["filename"]
    target_path = _resolve_model_target(model_entry["target_path"])
    size_gb = model_entry.get("size_gb", "?")
    display_name = model_entry.get("display_name", model_id)

    # Validate URL uses HTTPS
    if url.startswith("http://"):
        warn(f"Model URL uses HTTP (not HTTPS): {url}")
        print("  Downloading over unencrypted connection. Verify the hash after download.")

    # Validate filename
    if not filename.endswith(".gguf"):
        print(f"[ERROR] Invalid model filename: {filename} (must end in .gguf)")
        raise SystemExit(1)

    # Dry run
    if dry_run:
        print(f"\n  {Color.YELLOW}[DRY RUN]{Color.RESET} Would download model: {Color.CYAN}{display_name}{Color.RESET}")
        print(f"  URL:         {url}")
        print(f"  Target:      {target_path}")
        print(f"  Size:        {size_gb} GB")
        print(f"  License:     {model_entry.get('license_note', 'N/A')}")
        if model_entry.get("sha256"):
            print(f"  SHA256:      {model_entry['sha256'][:16]}...")
        if target_path.exists():
            print(f"  {Color.YELLOW}[NOTE]{Color.RESET} File already exists (use --force to redownload)")
        print()
        return

    # Check if already downloaded
    if target_path.exists():
        if not force:
            size_mb = target_path.stat().st_size / (1024 * 1024)
            print(f"\n  {Color.GREEN}Already downloaded:{Color.RESET} {target_path}")
            print(f"  Size: {size_mb:.1f} MB")
            print(f"  Use {Color.CYAN}--force{Color.RESET} to redownload.")
            return
        else:
            print(f"\n  {Color.YELLOW}[FORCE]{Color.RESET} Deleting existing file: {target_path}")
            target_path.unlink()

    # Create models/ directory if needed (user models dir)
    models_dir = Path(get_user_models_dir())
    models_dir.mkdir(parents=True, exist_ok=True)

    # Download with resume support
    print(f"\n  {Color.BOLD}Downloading:{Color.RESET} {Color.CYAN}{display_name}{Color.RESET}")
    print(f"  URL:    {url}")
    print(f"  Target: {target_path}")
    print(f"  Size:   {size_gb} GB")
    print()

    # Check for partial download (resume support)
    partial_path = target_path.with_suffix(target_path.suffix + ".part")
    resume_from = 0
    if partial_path.exists():
        resume_from = partial_path.stat().st_size
        if resume_from > 0:
            info(f"Resuming from {resume_from / (1024 * 1024):.1f} MB")

    try:
        headers = {}
        if resume_from > 0:
            headers["Range"] = f"bytes={resume_from}-"

        resp = requests.get(url, stream=True, timeout=30, headers=headers)
        resp.raise_for_status()

        # Check if server supports range requests
        if resume_from > 0 and resp.status_code != 206:
            info("Server does not support resume. Starting from beginning.")
            resume_from = 0
            partial_path.unlink(missing_ok=True)

        total_size = int(resp.headers.get("content-length", 0))
        if resume_from > 0 and resp.status_code == 206:
            total_size += resume_from

        downloaded = resume_from
        start_time = time.time()

        mode = "ab" if resume_from > 0 else "wb"
        with open(partial_path, mode) as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Show progress
                    if total_size > 0:
                        pct = downloaded / total_size * 100
                        downloaded_mb = downloaded / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        elapsed = time.time() - start_time
                        speed = downloaded_mb / elapsed if elapsed > 0 else 0
                        eta_s = (total_mb - downloaded_mb) / speed if speed > 0 else 0
                        print(
                            f"\r  Progress: {pct:5.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB) "
                            f"{speed:.1f} MB/s ETA: {eta_s:.0f}s",
                            end="",
                            flush=True,
                        )
                    else:
                        downloaded_mb = downloaded / (1024 * 1024)
                        print(
                            f"\r  Downloaded: {downloaded_mb:.1f} MB",
                            end="",
                            flush=True,
                        )

        elapsed = time.time() - start_time
        downloaded_mb = downloaded / (1024 * 1024)
        print()  # New line after progress

        # Rename partial to final
        if partial_path.exists():
            partial_path.rename(target_path)

        print(f"\n  {Color.GREEN}✓ Download complete{Color.RESET}")
        print(f"  Saved:     {target_path}")
        print(f"  Size:      {downloaded_mb:.1f} MB")
        if elapsed > 0:
            speed = downloaded_mb / elapsed
            print(f"  Speed:     {speed:.1f} MB/s")
        print(f"  Time:      {elapsed:.1f}s")

        # Verify hash if available
        if model_entry.get("sha256"):
            info("Verifying SHA256 hash...")
            actual_hash = _compute_sha256(target_path, progress=True)
            if actual_hash == model_entry["sha256"]:
                ok("SHA256 hash verified ✓")
            else:
                print(f"  {Color.RED}[FAIL]{Color.RESET} SHA256 mismatch!")
                print(f"  Expected: {model_entry['sha256']}")
                print(f"  Actual:   {actual_hash}")
                print("  The file may be corrupted. Try downloading again with --force.")

    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Download failed (HTTP {e.response.status_code}): {e}")
        # Keep partial for resume
        if partial_path.exists() and partial_path.stat().st_size == 0:
            partial_path.unlink()
        raise SystemExit(1) from None
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection failed. Check your internet connection.")
        # Keep partial for resume
        raise SystemExit(1) from None
    except KeyboardInterrupt:
        print(f"\n\n  {Color.YELLOW}[INTERRUPTED]{Color.RESET} Download cancelled.")
        # Keep partial for resume
        if partial_path.exists():
            print(f"  Partial download kept: {partial_path}")
            print("  Re-run to resume download.")
        raise SystemExit(1) from None
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        if partial_path.exists() and partial_path.stat().st_size == 0:
            partial_path.unlink()
        raise SystemExit(1) from None


def pull_all_models(dry_run: bool = False, force: bool = False):
    """Download all models from the registry (with confirmation)."""
    registry = load_models_registry()
    models = registry.get("models", [])

    if not models:
        print("\n  No models in registry.")
        return

    total_size = sum(m.get("size_gb", 0) for m in models)
    print(f"\n  {Color.BOLD}Download All Models{Color.RESET}")
    print(f"  Models: {len(models)} | Total size: {total_size:.1f} GB\n")

    for m in models:
        target = _resolve_model_target(m["target_path"])
        status = "✓" if target.exists() else " "
        print(f"  [{status}] {m['id']:<20} {m['display_name']} ({m['size_gb']} GB)")

    if not dry_run:
        try:
            response = input("\n  Download all? [y/N] ").strip().lower()
            if response not in ("y", "yes"):
                print("  Cancelled.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n  Cancelled.")
            return

    for m in models:
        target = _resolve_model_target(m["target_path"])
        if target.exists() and not force:
            info(f"Skipping {m['id']} (already downloaded)")
            continue
        print(f"\n  {'[DRY RUN] ' if dry_run else ''}Downloading {m['id']}...")
        pull_model(m["id"], dry_run=dry_run, force=force)


def scan_models_dir_for_gguf() -> list:
    """Scan models/ directories for .gguf files, return list of relative paths.

    Checks both user models dir and repo-root models/ dir.
    """
    found: list[str] = []
    user_models = get_user_models_dir()
    if user_models.exists():
        for f in user_models.glob("*.gguf"):
            found.append(str(f))

    # Also check repo-root models/
    repo_models = PROJECT_ROOT / "models"
    if repo_models.exists() and repo_models != user_models:
        for f in repo_models.glob("*.gguf"):
            path_str = str(f)
            if path_str not in found:
                found.append(path_str)

    return sorted(found)
