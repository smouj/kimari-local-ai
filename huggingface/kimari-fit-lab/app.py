"""Kimari Fit Lab — static GPU compatibility helper.

This Hugging Face Space does not execute models, download models, or use API keys.
It only maps user-provided hardware/context to safe Kimari Local AI suggestions.
"""

from __future__ import annotations

try:
    import gradio as gr
except ModuleNotFoundError:  # Allows local release tests without installing Gradio.

    class _DummyComponent:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def click(self, *args, **kwargs):
            return None

        def launch(self, *args, **kwargs):
            return None

    class _DummyThemes:
        @staticmethod
        def Soft():  # noqa: N802 - mirrors gradio.themes.Soft
            return None

    class _DummyGradio:
        Blocks = _DummyComponent
        Row = _DummyComponent
        Markdown = _DummyComponent
        Dropdown = _DummyComponent
        Number = _DummyComponent
        Radio = _DummyComponent
        Button = _DummyComponent
        Textbox = _DummyComponent
        themes = _DummyThemes()

    gr = _DummyGradio()

KIMARI_4B_STATUS = (
    "⚠️ Kimari-4B is **not released yet**. No public weights, adapters, or official GGUF files are available. "
    "Any Kimari-4B entry is a roadmap/private-pipeline reference only. Gate: **BLOCKED**."
)

GPU_PROFILES = {
    "NVIDIA GeForce GTX 1060 6GB": {
        "vram": 6,
        "profile": "gtx1060",
        "notes": "Validated locally with TinyLlama 1.1B Q4_K_M",
    },
    "NVIDIA GeForce GTX 1060 3GB": {"vram": 3, "profile": "test", "notes": "Small test models only"},
    "NVIDIA GeForce GTX 1080 8GB": {
        "vram": 8,
        "profile": "gtx1080",
        "notes": "Good for 7B Q4-class community GGUF models",
    },
    "NVIDIA GeForce RTX 2060 6GB": {"vram": 6, "profile": "gtx1060", "notes": "Similar VRAM class to GTX 1060 6GB"},
    "NVIDIA GeForce RTX 3060 12GB": {
        "vram": 12,
        "profile": "custom",
        "notes": "Comfortable for several 7B/8B Q4-class community GGUF models",
    },
    "NVIDIA GeForce RTX 4060 8GB": {
        "vram": 8,
        "profile": "gtx1080",
        "notes": "Good for 7B Q4-class community GGUF models",
    },
    "NVIDIA GeForce RTX 4090 24GB": {
        "vram": 24,
        "profile": "custom",
        "notes": "Large local-model experimentation headroom",
    },
    "Custom GPU": {"vram": 0, "profile": "custom", "notes": "Use the VRAM field below"},
}

MODEL_RECOMMENDATIONS = [
    ("TinyLlama 1.1B Q4_K_M", 1, 2, "recommended smoke-test model"),
    ("Qwen2.5 1.5B GGUF", 2, 3, "reference/community model, not official Kimari"),
    ("SmolLM2 1.7B GGUF", 2, 3, "reference/community model, not official Kimari"),
    ("Qwen2.5 3B GGUF", 3, 5, "reference/community model, not official Kimari"),
    ("Llama 3.2 3B GGUF", 3, 5, "reference/community model, not official Kimari"),
    ("Kimari-4B target", 4, 6, "not released; no weights or GGUF available"),
]


def _status_for_vram(vram_gb: float) -> tuple[str, str]:
    if vram_gb >= 6:
        return (
            "✅ Compatible",
            "Enough VRAM for the validated test flow and several small/medium community GGUF models.",
        )
    if vram_gb >= 3:
        return "⚠️ Borderline", "Use the test profile and small GGUF models first."
    return "❌ Limited", "Kimari may still run tiny CPU/GPU-offload tests, but this is below the practical CUDA target."


def _profile_for_vram(vram_gb: float, selected_profile: str) -> str:
    if selected_profile != "custom":
        return selected_profile
    if vram_gb >= 8:
        return "gtx1080"
    if vram_gb >= 6:
        return "gtx1060"
    return "test"


def _test_model_for_vram(vram_gb: float) -> str:
    if vram_gb >= 3:
        return "Qwen2.5 1.5B GGUF or TinyLlama 1.1B Q4_K_M"
    return "TinyLlama 1.1B Q4_K_M"


def build_recommendation(
    gpu_selection: str,
    custom_vram: float,
    ram_gb: float,
    os_name: str,
    user_level: str,
    goal: str,
) -> str:
    """Return a static compatibility report. No model execution happens here."""
    profile_data = GPU_PROFILES.get(gpu_selection, GPU_PROFILES["Custom GPU"])
    vram_gb = float(custom_vram or 0) if gpu_selection == "Custom GPU" else float(profile_data["vram"])
    if vram_gb <= 0:
        return "Please select a GPU or enter a positive VRAM value.\n\n" + KIMARI_4B_STATUS

    status, status_note = _status_for_vram(vram_gb)
    recommended_profile = _profile_for_vram(vram_gb, profile_data["profile"])
    test_model = _test_model_for_vram(vram_gb)
    ram_note = "✅ RAM looks fine for the local test flow." if ram_gb >= 8 else "⚠️ 8 GB+ system RAM is recommended."

    model_rows = ["| Model | VRAM guidance | Status |", "|---|---:|---|"]
    for model, minimum, recommended, note in MODEL_RECOMMENDATIONS:
        if vram_gb >= recommended:
            model_status = "✅ Recommended"
        elif vram_gb >= minimum:
            model_status = "⚠️ Borderline"
        else:
            model_status = "❌ Not recommended"
        model_rows.append(f"| {model} | {minimum}-{recommended} GB | {model_status} — {note} |")

    integration_hint = {
        "local chat": "Use the local endpoint directly or through a lightweight web UI.",
        "coding": "Generate Continue.dev config after the endpoint is running.",
        "open webui": "Use Open WebUI with base URL http://host.docker.internal:11435/v1 when running in Docker.",
        "openclaw": "Generate the OpenClaw local endpoint config and keep it localhost-only.",
        "continue.dev": "Generate Continue.dev config and point it at http://127.0.0.1:11435/v1.",
    }.get(goal.lower(), "Start with the local OpenAI-compatible endpoint.")

    install_hint = (
        "Use WSL2 instructions on Windows for best CUDA compatibility."
        if os_name == "Windows"
        else "Use the Linux/WSL2 install path with NVIDIA drivers and llama.cpp CUDA."
    )
    if os_name == "WSL2":
        install_hint = "Use WSL2 with NVIDIA passthrough; verify nvidia-smi and llama-server CUDA."

    return "\n".join(
        [
            f"## Compatibility: {status}",
            f"**GPU**: {gpu_selection}",
            f"**OS**: {os_name}",
            f"**VRAM**: {vram_gb:g} GB",
            f"**RAM**: {ram_gb:g} GB — {ram_note}",
            f"**User level**: {user_level}",
            f"**Goal**: {goal}",
            f"**Recommended profile**: `{recommended_profile}`",
            f"**Recommended test model**: {test_model}",
            f"**Hardware note**: {profile_data['notes']}. {status_note}",
            "",
            "### Model compatibility",
            *model_rows,
            "",
            "### Safe install / endpoint commands",
            "```bash",
            "kimari doctor --deep",
            "kimari pull test",
            f"kimari start --profile {recommended_profile}",
            "kimari integrations validate --base-url http://127.0.0.1:11435/v1 --json",
            "kimari integrations generate --all --json --profile test",
            "```",
            "",
            "### Integration hint",
            integration_hint,
            "",
            "### Install hint",
            install_hint,
            "",
            KIMARI_4B_STATUS,
            "",
            "This Space is static: no API key, no model execution, no model download.",
        ]
    )


def get_commands() -> str:
    """Return baseline safe commands for the Space UI."""
    return """kimari doctor --deep
kimari pull test
kimari start --profile test
kimari integrations validate --base-url http://127.0.0.1:11435/v1 --json
kimari integrations generate --all --json --profile test
kimari stop"""


with gr.Blocks(title="Kimari Fit Lab", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🔬 Kimari Fit Lab
        Static compatibility helper for Kimari Local AI.

        This tool does **not** run models, download models, or use API keys.
        """
    )

    with gr.Row():
        gpu_dropdown = gr.Dropdown(choices=list(GPU_PROFILES.keys()), value="NVIDIA GeForce GTX 1060 6GB", label="GPU")
        os_dropdown = gr.Dropdown(choices=["Windows", "WSL2", "Linux"], value="WSL2", label="OS")

    with gr.Row():
        custom_vram = gr.Number(label="Custom VRAM (GB)", value=6, minimum=1, maximum=96, step=1)
        ram_input = gr.Number(label="System RAM (GB)", value=16, minimum=4, maximum=256, step=1)

    with gr.Row():
        user_level = gr.Radio(choices=["beginner", "technical", "advanced"], value="technical", label="User level")
        goal = gr.Dropdown(
            choices=["local chat", "coding", "Open WebUI", "OpenClaw", "Continue.dev"],
            value="local chat",
            label="Goal",
        )

    check_btn = gr.Button("Check Compatibility", variant="primary")
    result = gr.Markdown()
    check_btn.click(
        fn=build_recommendation,
        inputs=[gpu_dropdown, custom_vram, ram_input, os_dropdown, user_level, goal],
        outputs=result,
    )

    gr.Markdown("### Baseline commands")
    gr.Textbox(value=get_commands(), label="", interactive=False, lines=7)

    gr.Markdown(
        """
        ---
        **Kimari Local AI** is an open-source framework for local GGUF inference on consumer NVIDIA GPUs.

        - GitHub: https://github.com/smouj/kimari-local-ai
        - Docs: https://smouj.github.io/kimari-local-ai/
        - Kimari-4B is **not released yet**. No public weights, adapters, or official GGUF files are available.
        - Gate: **BLOCKED**
        """
    )


if __name__ == "__main__":
    demo.launch()
