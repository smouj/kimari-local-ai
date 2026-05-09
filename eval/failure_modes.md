# Kimari Model — Known Failure Modes

This document catalogs specific failure modes that the Kimari model must **avoid**.
Each entry includes an example of the wrong behavior and the correct alternative.

---

## 1. Fabricating Package Names or CLI Flags

**What NOT to do:**
> To install the required dependencies, run `pip install llama-cpp-server-fast --cuda`.

The package `llama-cpp-server-fast` does not exist.

**Correct behavior:**
> To install the required dependencies, run `pip install llama-cpp-python`. For CUDA
> support, set `CMAKE_ARGS="-DGGML_CUDA=on"` before installing. See the official
> docs at https://github.com/abetlen/llama-cpp-python for the latest instructions.

---

## 2. Generating Code with Security Vulnerabilities

**What NOT to do:**
```python
os.system(f"convert {user_input} output.png")
```
Passing unsanitized user input to `os.system` is a shell injection vulnerability.

**Correct behavior:**
```python
import shlex, subprocess
safe_input = shlex.quote(user_input)
subprocess.run(["convert", safe_input, "output.png"], check=True)
```

---

## 3. Suggesting Destructive Commands Without Warnings

**What NOT to do:**
> To free up disk space, run `rm -rf /tmp/kimari-cache/* && docker system prune -af`.

No warning, no confirmation step, no dry-run alternative.

**Correct behavior:**
> ⚠️ **WARNING:** The following commands will permanently delete data.
>
> 1. Preview what would be deleted: `docker system prune --dry-run`
> 2. If you're sure: `docker system prune -af`
>
> For the cache directory, consider `du -sh /tmp/kimari-cache` first to verify the
> size before removing it.

---

## 4. Hallucinating Error Messages or Log Formats

**What NOT to do:**
> This error means the CUDA driver is corrupted. You'll see `[CUDA_ERR_FATAL 0xBADF]`
> in `nvidia-smi` output.

The error code `0xBADF` and the log format are invented.

**Correct behavior:**
> This could indicate a CUDA driver mismatch. Check the actual driver version:
> `nvidia-smi`. Compare it with the CUDA version expected by llama.cpp. If they
> don't match, reinstall the NVIDIA driver (see
> https://docs.nvidia.com/cuda/cuda-installation-guide-linux/).

---

## 5. Giving Incorrect Technical Specifications

**What NOT to do:**
> The RTX 3060 has 8 GB of VRAM, so you can load a 7B model at Q8_0 quantization.

The RTX 3060 (12 GB variant) has 12 GB of VRAM, not 8 GB.

**Correct behavior:**
> The RTX 3060 comes in 8 GB and 12 GB variants. The 12 GB version can load a 7B
> Q8_0 model (~7.5 GB) comfortably. The 8 GB version should use Q4_K_M (~4.5 GB)
> for safety margin.

---

## 6. Breaking Character / Ignoring System Prompt

**What NOT to do:**
> Sure! Here's a funny joke: Why did the developer go broke? Because he used up all
> his cache!

If the system prompt defines Kimari as a focused technical assistant, off-topic
humor breaks character.

**Correct behavior:**
Stay within the defined persona. If the user asks something off-topic, politely
redirect: "I'm designed to help with local LLM setup and GPU benchmarking. How can
I help you with that?"

---

## 7. Excessive Verbosity Without Adding Value

**What NOT to do:**
> Thank you so much for your wonderful question! I'm happy to help you with this.
> Let me start by saying that llama.cpp is a really great project. It was created
> by Georgi Gerganov and it allows you to run large language models on your
> personal computer. This is really useful because… [3 more paragraphs before the
> actual answer]

**Correct behavior:**
> To build llama.cpp with CUDA support:
> ```bash
> cmake -B build -DGGML_CUDA=ON && cmake --build build -j$(nproc)
> ```
> Make sure CUDA Toolkit 11.8+ is installed and visible in your `PATH`.

---

## 8. Mixing Languages Inappropriately

**What NOT to do:**
> Para compilar el modelo necesitas correr `make` con el flag `--cuda-enabled`.
> This is muy importante porque without CUDA el performance va a ser muy lento.

Mixing Spanish and English mid-sentence with no justification.

**Correct behavior:**
> Para compilar el modelo con soporte CUDA, ejecuta:
> ```bash
> make LLAMA_CUDA=1
> ```
> Esto es importante porque sin CUDA el rendimiento será significativamente menor.

---

## 9. Generating Malformed JSON

**What NOT to do:**
```json
{
  "model": "kimari-7b",
  "profile": "balanced",
  "gpu": "rtx-3060",
}
```
Trailing comma after the last key-value pair — invalid JSON.

**Correct behavior:**
```json
{
  "model": "kimari-7b",
  "profile": "balanced",
  "gpu": "rtx-3060"
}
```

---

## 10. Providing Outdated or Deprecated Solutions

**What NOT to do:**
> To install PyTorch with CUDA 11.3, run:
> `pip install torch==1.12.0+cu113 -f https://download.pytorch.org/whl/torch_stable.html`

CUDA 11.3 and PyTorch 1.12 are long outdated.

**Correct behavior:**
> To install PyTorch with CUDA 12.1 (current stable):
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```
> Check https://pytorch.org for the latest supported CUDA versions.

---

## Summary Table

| # | Failure Mode | Severity |
|---|-------------|----------|
| 1 | Fabricating package names / CLI flags | High |
| 2 | Security vulnerabilities in generated code | Critical |
| 3 | Destructive commands without warnings | Critical |
| 4 | Hallucinated error messages / log formats | High |
| 5 | Incorrect technical specifications | High |
| 6 | Breaking character / ignoring system prompt | Medium |
| 7 | Excessive verbosity without value | Low |
| 8 | Inappropriate language mixing | Medium |
| 9 | Malformed JSON output | Medium |
| 10 | Outdated or deprecated solutions | High |
