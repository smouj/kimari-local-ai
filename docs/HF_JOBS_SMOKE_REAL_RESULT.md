# HF Jobs Smoke Real Result

> **Completed on 2026-05-12** — HF Jobs smoke test verified working.

## Jobs Submitted

| Job ID | Flavor | Image | Status | GPU | CUDA |
|--------|--------|-------|--------|-----|------|
| `6a036dd77251...` | a10g-small | python:3.12-slim | ✅ COMPLETED | N/A (no torch) | N/A |
| `6a036f1a7618...` | a10g-small | pytorch:2.1.0-cuda12.1 | ✅ COMPLETED | NVIDIA A10G 22.3 GB | 12.1 |

## Smoke Results

### Job 1: python:3.12-slim

```json
{
  "smoke": true,
  "python": "3.12.13 (main, May  8 2026, 20:07:16) [GCC 14.2.0]",
  "training_performed": false,
  "gate_state": "BLOCKED"
}
```

- Python runs on a10g-small
- No torch in slim image (expected)
- **No training performed**

### Job 2: pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel

```json
{
  "smoke": true,
  "python": "3.10.13",
  "platform": "linux",
  "torch_version": "2.1.0",
  "cuda_available": true,
  "gpu_name": "NVIDIA A10G",
  "gpu_count": 1,
  "cuda_version": "12.1",
  "gpu_vram_gb": 22.3,
  "training_performed": false,
  "adapter_generated": false,
  "gate_state": "BLOCKED"
}
```

- ✅ **CUDA available**: true
- ✅ **GPU detected**: NVIDIA A10G with 22.3 GB VRAM
- ✅ **PyTorch**: 2.1.0 with CUDA 12.1
- ✅ **No training performed**
- ✅ **No adapter generated**

## What Was NOT Done

- ❌ No training was performed
- ❌ No adapter was created
- ❌ No GGUF was generated
- ❌ No model was uploaded to Hugging Face
- ❌ No checkpoints were created
- ❌ No raw logs were committed
- ❌ No billing/plan information was captured

## Cost

- Flavor: a10g-small ($1.00/hour)
- Runtime: ~1-2 minutes each
- Estimated total cost: ~$0.05

## Conclusion

HF Jobs **works** and can access GPU infrastructure. The a10g-small flavor provides an NVIDIA A10G with 22.3 GB VRAM, which is sufficient for LoRA training on a 3B parameter model.

**Next step**: v0.1.49-alpha — micro SFT real on HF Jobs (if gate advances).

**Gate**: BLOCKED