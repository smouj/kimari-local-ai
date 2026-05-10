"""
Kimari Experimental API — FastAPI application factory and endpoint definitions.

**WARNING**: This API is EXPERIMENTAL. Endpoints, schemas, and behavior
may change without notice between alpha releases.

This module defines all endpoints for the Kimari management API.
It shares backend logic with the CLI — no business logic is duplicated.

Rules:
- No real process control yet (start/stop return 501).
- No secrets exposed in responses.
- No model downloads.
- Uses existing CLI/config/performance functions when safe.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from kimari import __version__ as KIMARI_VERSION  # noqa: N812
from kimari.api.schemas import (
    ConfigResponse,
    HealthResponse,
    ModelEntry,
    ModelsResponse,
    OptimizeRequest,
    OptimizeResponse,
    PerfDryRunRequest,
    PerfDryRunResponse,
    PerfModeResult,
    ProfileDetail,
    ProfilesResponse,
    ServerStartRequest,
    StatusResponse,
)


def build_app() -> FastAPI:
    """Build and configure the FastAPI application.

    This function is the single entry point for creating the app.
    All routes, middleware, and exception handlers are registered here.
    """
    app = FastAPI(
        title="Kimari Local AI — Experimental API",
        description=(
            "**EXPERIMENTAL** — This API is under active development. "
            "Do NOT build clients against these endpoints yet. "
            "Schemas and behavior may change without notice.\n\n"
            "Install with: `pip install 'kimari-local-ai[api]'`\n"
            "Start with: `kimari api --experimental`"
        ),
        version=KIMARI_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Middleware ──────────────────────────────────────────────────────
    # Experimental auth middleware
    @app.middleware("http")
    async def experimental_auth_middleware(request: Request, call_next):
        """Experimental Bearer token auth.

        Behavior:
        - host=127.0.0.1: auth is permissive (token accepted if present, no error if missing).
        - host!=127.0.0.1: auth is required; missing/invalid token -> 401.
        - GET /health is always accessible.
        """
        # Health endpoint is always accessible
        if request.url.path == "/health":
            return await call_next(request)

        # Check if auth is required (non-localhost)
        host_header = request.headers.get("host", "")
        is_localhost = host_header.startswith("127.0.0.1") or host_header.startswith("localhost")

        if not is_localhost:
            # Non-localhost: require Bearer token
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Unauthorized", "detail": "Bearer token required for non-localhost access"},
                )
            # Validate token against local store
            token_value = auth_header[7:]  # strip "Bearer "
            from kimari.security.tokens import show_token

            stored = show_token()
            if stored is None or stored.get("token") != token_value:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Unauthorized", "detail": "Invalid or missing token"},
                )

        return await call_next(request)

    # ── Routes ─────────────────────────────────────────────────────────

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        """Health check — always accessible, no auth required."""
        return HealthResponse(status="ok", version=KIMARI_VERSION)

    @app.get("/status", response_model=StatusResponse, tags=["status"])
    async def status() -> StatusResponse:
        """Server status — equivalent to ``kimari status --json``."""
        from kimari.core.state import is_pid_alive, read_state

        state = read_state() or {}
        running = False
        pid = state.get("pid")
        if pid and is_pid_alive(pid):
            running = state.get("status") == "READY"
        elif state.get("status") == "READY":
            running = False  # process died

        return StatusResponse(
            running=running,
            pid=pid if running else None,
            profile=state.get("profile"),
            model=state.get("model"),
            host=state.get("host"),
            port=state.get("port"),
            uptime_s=None,  # computed on demand
            health=None,
        )

    @app.get("/config", response_model=ConfigResponse, tags=["config"])
    async def config() -> ConfigResponse:
        """Current configuration — equivalent to ``kimari config show --json``."""
        from kimari.config.loader import get_config_path, load_config

        cfg = load_config()
        profiles_list = []
        for name, p in cfg.get("profiles", {}).items():
            profiles_list.append(
                {
                    "name": name,
                    "model": p.get("model", ""),
                    "host": p.get("host", "127.0.0.1"),
                    "port": p.get("port", 11435),
                    "ctx": p.get("ctx"),
                    "quantization": p.get("quantization", ""),
                    "estimated_model_size_gb": p.get("estimated_model_size_gb"),
                }
            )

        return ConfigResponse(
            config_version=cfg.get("config_version", 3),
            default_profile=cfg.get("default_profile", "test"),
            profiles=profiles_list,
            config_path=str(get_config_path()) if get_config_path() else None,
        )

    @app.get("/profiles", response_model=ProfilesResponse, tags=["profiles"])
    async def profiles() -> ProfilesResponse:
        """List available GPU profiles — equivalent to ``kimari profiles --json``."""
        from kimari.config.loader import load_config

        cfg = load_config()
        profile_list = []
        for name, p in cfg.get("profiles", {}).items():
            profile_list.append(
                ProfileDetail(
                    name=name,
                    model=p.get("model", ""),
                    host=p.get("host", "127.0.0.1"),
                    port=p.get("port", 11435),
                    ctx=p.get("ctx"),
                    batch=p.get("batch"),
                    ubatch=p.get("ubatch"),
                    gpu_layers=p.get("gpu_layers"),
                    flash_attn=p.get("flash_attn"),
                    parallel=p.get("parallel"),
                )
            )

        return ProfilesResponse(
            default_profile=cfg.get("default_profile", "test"),
            profiles=profile_list,
        )

    @app.get("/models", response_model=ModelsResponse, tags=["models"])
    async def models() -> ModelsResponse:
        """List available models — equivalent to ``kimari models --json``."""
        from kimari.models.registry import get_effective_models_registry, scan_models_dir_for_gguf

        registry = get_effective_models_registry()
        local_ggufs = set(scan_models_dir_for_gguf())
        model_list = []
        for m in registry.get("models", []):
            filename = m.get("target_path", "").split("/")[-1] if m.get("target_path") else m.get("id", "")
            model_list.append(
                ModelEntry(
                    id=m.get("id", ""),
                    display_name=m.get("display_name", m.get("id", "")),
                    filename=filename,
                    size_gb=m.get("expected_vram_gb"),
                    status=m.get("status"),
                    downloaded=filename in local_ggufs,
                    sha256_pinned=m.get("sha256") is not None,
                )
            )

        return ModelsResponse(models=model_list)

    @app.post(
        "/optimize",
        response_model=OptimizeResponse,
        tags=["optimize"],
    )
    async def optimize(request: OptimizeRequest) -> OptimizeResponse:
        """Get optimization recommendations — equivalent to ``kimari optimize --json``."""
        from kimari.config.loader import get_profile, load_config
        from kimari.performance import recommend_profile_settings

        cfg = load_config()
        profile_name = request.profile or cfg.get("default_profile", "test")
        profile = get_profile(cfg, profile_name)
        model_size_gb = profile.get("estimated_model_size_gb", 1.0)
        vram_total_gb = request.vram_gb or profile.get("vram_total_gb", 6.0)
        mode = request.mode

        settings = recommend_profile_settings(vram_total_gb, model_size_gb, mode)

        return OptimizeResponse(
            profile=profile_name,
            recommendations={
                "ctx": settings["ctx"],
                "batch": settings["batch"],
                "ubatch": settings["ubatch"],
                "cache_type_k": settings["cache_type_k"],
                "cache_type_v": settings["cache_type_v"],
                "gpu_layers": settings["gpu_layers"],
                "flash_attn": settings["flash_attn"],
                "parallel": settings["parallel"],
            },
            estimates={
                "expected_vram_gb": settings["expected_vram_gb"],
                "expected_ram_gb": settings["expected_ram_gb"],
            },
            confidence=settings["confidence"],
            warnings=settings["warnings"],
        )

    @app.post(
        "/perf/dry-run",
        response_model=PerfDryRunResponse,
        tags=["perf"],
    )
    async def perf_dry_run(request: PerfDryRunRequest) -> PerfDryRunResponse:
        """Performance dry-run — equivalent to ``kimari perf --dry-run --json``."""
        from kimari.config.loader import get_profile, load_config
        from kimari.performance import recommend_profile_settings

        cfg = load_config()
        profile_name = request.profile or cfg.get("default_profile", "test")
        profile = get_profile(cfg, profile_name)
        model_size_gb = profile.get("estimated_model_size_gb", 1.0)
        vram_total_gb = profile.get("vram_total_gb", 6.0)

        modes = (
            ["safe", "balanced", "fast", "ide", "agent"]
            if request.matrix
            else [profile.get("performance_mode", "balanced")]
        )

        results = []
        for mode in modes:
            s = recommend_profile_settings(vram_total_gb, model_size_gb, mode)
            results.append(
                PerfModeResult(
                    mode=mode,
                    ctx=s["ctx"],
                    batch=s["batch"],
                    ubatch=s["ubatch"],
                    cache_type_k=s["cache_type_k"],
                    cache_type_v=s["cache_type_v"],
                    gpu_layers=s["gpu_layers"],
                    flash_attn=s["flash_attn"],
                    parallel=s["parallel"],
                    expected_vram_gb=s["expected_vram_gb"],
                    expected_ram_gb=s["expected_ram_gb"],
                    confidence=s["confidence"],
                    warnings=s["warnings"],
                )
            )

        return PerfDryRunResponse(
            profile=profile_name,
            model=profile.get("model", ""),
            vram_total_gb=vram_total_gb,
            dry_run=True,
            modes=results,
        )

    # ── Planned endpoints (501 Not Implemented) ──────────────────────

    @app.post(
        "/server/start",
        status_code=501,
        tags=["server"],
        summary="Start server (planned)",
    )
    async def server_start(request: ServerStartRequest) -> dict[str, str]:
        """Start llama-server with a profile — **NOT YET IMPLEMENTED**.

        This endpoint is planned for a future release.
        Currently returns 501 Not Implemented.
        """
        return {
            "status": "planned",
            "detail": "Server start via API is planned for a future release. Use 'kimari start' for now.",
        }

    @app.post(
        "/server/stop",
        status_code=501,
        tags=["server"],
        summary="Stop server (planned)",
    )
    async def server_stop() -> dict[str, str]:
        """Stop llama-server — **NOT YET IMPLEMENTED**.

        This endpoint is planned for a future release.
        Currently returns 501 Not Implemented.
        """
        return {
            "status": "planned",
            "detail": "Server stop via API is planned for a future release. Use 'kimari stop' for now.",
        }

    return app
