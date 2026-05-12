"""Kimari Fit Lab — GPU Compatibility Checker.

A Gradio app that checks if your GPU is compatible with Kimari Local AI.
This Space does NOT run any model. It is a static lookup tool.

Rules:
- No model execution
- No model downloads
- No API keys
- No claims that Kimari-4B is released
"""

import gradio as gr

# GPU compatibility data (VRAM-based recommendations)
GPU_PROFILES = {
    "NVIDIA GeForce GTX 1060 6GB": {"vram": 6, "status": "compatible", "profile": "gtx1060", "notes": "Validated locally with TinyLlama 1.1B Q4_K_M"},
    "NVIDIA GeForce GTX 1060 3GB": {"vram": 3, "status": "borderline", "profile": "test", "notes": "May work with small models only (TinyLlama)"},
    "NVIDIA GeForce GTX 1080 8GB": {"vram": 8, "status": "compatible", "profile": "gtx1080", "notes": "Good for 7B Q4 models"},
    "NVIDIA GeForce RTX 2060 6GB": {"vram": 6, "status": "compatible", "profile": "gtx1060", "notes": "Similar to GTX 1060 6GB"},
    "NVIDIA GeForce RTX 3060 12GB": {"vram": 12, "status": "compatible", "profile": "custom", "notes": "Excellent for 7B-13B models"},
    "NVIDIA GeForce RTX 4060 8GB": {"vram": 8, "status": "compatible", "profile": "gtx1080", "notes": "Good for 7B models"},
    "NVIDIA GeForce RTX 4090 24GB": {"vram": 24, "status": "compatible", "profile": "custom", "notes": "Excellent for large models"},
    "Custom GPU": {"vram": 0, "status": "unknown", "profile": "test", "notes": "Enter your VRAM to check"},
}

MODEL_RECOMMENDATIONS = {
    "TinyLlama 1.1B Q4_K_M": {"min_vram": 1, "recommended_vram": 2, "type": "test"},
    "Qwen2.5 1.5B Q4_K_M": {"min_vram": 1.5, "recommended_vram": 3, "type": "inference"},
    "Qwen2.5 3B Q4_K_M": {"min_vram": 2.5, "recommended_vram": 5, "type": "inference"},
    "Llama 3.2 3B Q4_K_M": {"min_vram": 2.5, "recommended_vram": 5, "type": "inference"},
    "Kimari-4B (target)": {"min_vram": 3.5, "recommended_vram": 6, "type": "target"},
    "Llama 3.1 8B Q4_K_M": {"min_vram": 5.5, "recommended_vram": 8, "type": "inference"},
}

KIMARI_4B_STATUS = (
    "⚠️ Kimari-4B is **not released yet**. No weights, adapters, or GGUF files are available. "
    "The 'Kimari-4B (target)' entry shows the planned VRAM requirement, not a download link."
)


def check_gpu(gpu_selection: str, custom_vram: int) -> str:
    """Check GPU compatibility and return recommendations."""
    if gpu_selection == "Custom GPU" and custom_vram > 0:
        profile = {"vram": custom_vram, "status": "compatible", "profile": "custom", "notes": "Custom VRAM specified"}
        vram = custom_vram
    elif gpu_selection in GPU_PROFILES:
        profile = GPU_PROFILES[gpu_selection]
        vram = profile["vram"]
    else:
        return "Please select a GPU or enter custom VRAM."

    result_lines = [
        f"## GPU: {gpu_selection}",
        f"**VRAM**: {vram} GB",
        f"**Status**: {profile['status'].title()}",
        f"**Recommended Profile**: `--profile {profile['profile']}`",
        f"**Notes**: {profile['notes']}",
        "",
        "### Model Compatibility",
        "",
        "| Model | Min VRAM | Status |",
        "|-------|----------|--------|",
    ]

    for model, rec in MODEL_RECOMMENDATIONS.items():
        min_v = rec["min_vram"]
        if vram >= rec["recommended_vram"]:
            status = "✅ Recommended"
        elif vram >= min_v:
            status = "⚠️ Borderline"
        else:
            status = "❌ Not recommended"
        result_lines.append(f"| {model} | {min_v} GB | {status} |")

    result_lines.extend(["", KIMARI_4B_STATUS, "", "---", "Gate: **BLOCKED** | No weights published"])

    return "\n".join(result_lines)


def get_commands() -> str:
    """Return recommended Kimari commands."""
    return """```bash
# Check your environment
kimari doctor --deep

# Download test model
kimari pull test

# Start with test profile (TinyLlama 1.1B)
kimari start --profile test

# Validate endpoint
kimari integrations validate --base-url http://127.0.0.1:11435/v1 --json

# Generate integration configs
kimari integrations generate --all --json --profile test

# Stop server
kimari stop
```"""


with gr.Blocks(
    title="Kimari Fit Lab",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown(
        """
        # 🔬 Kimari Fit Lab
        Check if your GPU is compatible with Kimari Local AI.

        This tool does **not** run any model. It is a static lookup based on VRAM requirements.
        """
    )

    with gr.Row():
        gpu_dropdown = gr.Dropdown(
            choices=list(GPU_PROFILES.keys()),
            value="NVIDIA GeForce GTX 1060 6GB",
            label="Select your GPU",
        )
        custom_vram = gr.Number(
            label="Custom VRAM (GB)",
            value=6,
            minimum=1,
            maximum=48,
            step=1,
        )

    check_btn = gr.Button("Check Compatibility", variant="primary")
    result = gr.Markdown()

    check_btn.click(
        fn=check_gpu,
        inputs=[gpu_dropdown, custom_vram],
        outputs=result,
    )

    gr.Markdown("### Recommended Commands")
    cmd_output = gr.Textbox(
        value=get_commands(),
        label="",
        interactive=False,
        lines=10,
    )

    gr.Markdown(
        """
        ---
        **Kimari Local AI** is an open-source framework for running local LLMs on consumer NVIDIA GPUs.

        - 🔗 [GitHub](https://github.com/smouj/kimari-local-ai)
        - 📄 [Documentation](https://smouj.github.io/kimari-local-ai/)
        - ⚠️ Kimari-4B is **not released yet**. No public weights available.
        - Gate: **BLOCKED**
        """
    )


if __name__ == "__main__":
    demo.launch()