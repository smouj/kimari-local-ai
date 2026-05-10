# Model Hashing

Kimari provides SHA-256 hashing and verification for GGUF model files. This ensures the integrity of downloaded models and lets you confirm that a model file matches a known-good hash from the registry.

---

## Commands

### Compute a Hash

```bash
kimari models hash <path>
```

Computes the SHA-256 hash of a local GGUF file. The file must exist on disk.

**Example:**

```bash
kimari models hash ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

**Output:**

```
  Model Hash
  Path:   ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Size:   661.6 MB (693,792,256 bytes)
  SHA256: eab1df1c6c...
```

**JSON output:**

```bash
kimari models hash --json ./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

Returns structured JSON:

```json
{
  "path": "./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
  "sha256": "eab1df1c6c...",
  "size_bytes": 693792256,
  "file_exists": true
}
```

If the file does not exist, `file_exists` will be `false` and `sha256` will be `null`.

---

### Verify Against Registry

```bash
kimari models verify <model-id>
```

Verifies a model's SHA-256 hash against the hash stored in the model registry.

**Example:**

```bash
kimari models verify test
```

**Possible outcomes:**

| Outcome | Meaning |
|---|---|
| **Verified** | The computed hash matches the registry hash. |
| **Mismatch** | The computed hash does NOT match. The file may be corrupted. |
| **Not pinned** | No SHA-256 is defined in the registry for this model. The computed hash is shown but cannot be compared. |
| **File not found** | The model file does not exist on disk. |

**Verify all models:**

```bash
kimari models verify --all --json
```

This iterates through every model in the registry and reports the verification status for each, outputting structured JSON.

---

### Pin a Hash to User Registry

```bash
kimari models pin-hash <model-id> --write --yes
```

Pins the computed SHA-256 hash of a model to the **user-level** models registry. This is useful when:

- A model has no hash in the default registry.
- You want to lock a specific file's hash for future verification.

**Dry run (default):**

```bash
kimari models pin-hash test
```

Shows what would be written without actually modifying the registry.

**Write for real:**

```bash
kimari models pin-hash test --write --yes
```

The `--write` flag enables writing. The `--yes` flag skips the interactive confirmation prompt (required in non-interactive/CI environments).

**Behavior:**

- A backup of the existing user registry is created before writing.
- The hash is computed from the local file — no invented hashes are used.
- If the model file does not exist, the command fails with an error.
- In non-interactive mode (no TTY), `--yes` is required; the command refuses to write without it.

---

## How to Compute the Hash of a Real GGUF

The hash is computed by reading the **entire file** byte-by-byte using Python's `hashlib.sha256()`:

1. The file is opened in binary mode.
2. It is read in 8192-byte chunks.
3. Each chunk is fed to the SHA-256 hasher.
4. The final hex digest is the model's hash.

This is a standard SHA-256 computation — no truncation, no prefix-only hashing. The entire GGUF file is hashed, including headers, metadata, and tensor data.

**Important:** This means the hash depends on the exact file contents. Two GGUF files with the same model but different quantization, different metadata, or even different padding bytes will have different hashes.

---

## How to Pin Only If the File Exists

The `pin-hash` command **requires the file to exist**. If the model file is not found on disk, the command returns an error and does not write anything:

```bash
$ kimari models pin-hash nonexistent-model --write --yes
[ERROR] Model file not found: /home/user/.local/share/kimari/models/nonexistent.gguf
```

This is intentional — you cannot pin a hash for a file you don't have. The hash must be computed from the actual file.

If you want to check whether a model exists before pinning:

```bash
kimari models list --json | jq '.[] | select(.id == "test") | .downloaded'
```

---

## How to Avoid Invented Hashes

**Never manually type or invent a SHA-256 hash.** A hash that was not computed from the actual file is worse than no hash at all — it will cause false mismatch errors.

Rules:

1. **Only use hashes computed by `kimari models hash` or `kimari models pin-hash`.** These commands compute the hash from the actual file on disk.
2. **Never copy-paste a hash from a third party** unless you trust the source and can independently verify it.
3. **Never put a placeholder hash** (like `0000...0000` or `TODO`) in the registry. If no hash is available, omit the `sha256` field entirely.
4. **Never fabricate a hash** to make CI pass. If verification fails, investigate the mismatch.

If you need to report a hash in a PR (see below), always compute it using the CLI command.

---

## How to Report Hashes in PRs

When contributing a new model entry or updating a model's hash, include the hash in your PR description:

1. **Compute the hash** using the CLI:
   ```bash
   kimari models hash --json ./models/your-model.Q4_K_M.gguf
   ```

2. **Include the full command output** in the PR description so reviewers can verify the method used.

3. **Do not include the model file itself.** GGUF files are large and must not be committed to the repository.

4. **Reference the model's source URL** (e.g. Hugging Face) so reviewers can independently download and verify the hash.

5. **State the model's license** so maintainers can confirm it is permissible to include in the registry.

Example PR description:

```
## Add model: Qwen3-4B-Q5_K_M

- Source: https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/main/qwen3-4b-q5_k_m.gguf
- License: Apache-2.0
- Hash computed via: `kimari models hash --json ./models/qwen3-4b-q5_k_m.gguf`
- SHA-256: <actual hash from command output>
- Size: 3.8 GB
```

---

## Privacy: Don't Upload Models Without Permission

**Do not upload, share, or redistribute GGUF model files unless the model's license explicitly permits it.**

- Some models (e.g., LLaMA-derived) have licenses that restrict redistribution.
- The Kimari registry stores **metadata** (filename, URL, hash) — not the model files themselves.
- When running `kimari models hash` or `kimari models pin-hash`, the hash is computed **locally**. No data is sent to any server.
- When reporting hashes in PRs, you are sharing only the hash value and metadata — never the model file.

If a model's license does not permit redistribution:

- Include the **download URL** in the registry so users can obtain the model themselves.
- Include the **hash** so users can verify their download.
- Do **not** host the model file or include it in the repository.

---

## Command Reference

| Command | Description |
|---|---|
| `kimari models hash <path>` | Compute SHA-256 of a local GGUF file |
| `kimari models hash --json <path>` | Compute SHA-256 with JSON output |
| `kimari models verify <model-id>` | Verify model hash against registry |
| `kimari models verify --all --json` | Verify all models, JSON output |
| `kimari models pin-hash <model-id>` | Dry-run: show what hash would be pinned |
| `kimari models pin-hash <model-id> --write` | Pin hash (prompts for confirmation) |
| `kimari models pin-hash <model-id> --write --yes` | Pin hash (skip confirmation) |

---

*Model hashing is part of Kimari Local AI v0.1.16-alpha. Hash algorithms and registry format may evolve before a stable release.*
