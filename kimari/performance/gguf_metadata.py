"""
Lightweight GGUF metadata reader for Kimari.

Reads model architecture metadata from GGUF files without loading the
entire model. Uses only Python stdlib (struct, pathlib).

No external dependencies. No network calls. No side effects beyond file I/O.
Fails gracefully on corrupt or missing files — always returns safe defaults.
"""

import contextlib
import struct
from pathlib import Path

# GGUF value type constants
GGUF_TYPE_UINT8 = 0
GGUF_TYPE_INT8 = 1
GGUF_TYPE_UINT16 = 2
GGUF_TYPE_INT16 = 3
GGUF_TYPE_UINT32 = 4
GGUF_TYPE_INT32 = 5
GGUF_TYPE_FLOAT32 = 6
GGUF_TYPE_BOOL = 7
GGUF_TYPE_STRING = 8
GGUF_TYPE_ARRAY = 9
GGUF_TYPE_UINT64 = 10
GGUF_TYPE_INT64 = 11
GGUF_TYPE_FLOAT64 = 12

# Metadata keys to extract (with fallback default values)
_METADATA_KEYS: dict[str, str] = {
    "llama.attention.layer_count": "n_layer",
    "llama.embedding_length": "n_embd",
    "llama.attention.head_count": "n_head",
    "llama.context_length": "context_length",
    "general.architecture": "architecture",
}

# Safe defaults when parsing fails
_DEFAULTS: dict = {
    "file_size_bytes": 0,
    "n_layer": 32,
    "n_embd": 3200,
    "n_head": 32,
    "context_length": 4096,
    "architecture": "unknown",
    "parse_success": False,
}


def _read_string(data: bytes, offset: int) -> tuple[str, int]:
    """Read a GGUF string (uint64 length + bytes) from data at offset.

    Returns (string_value, new_offset).
    """
    if offset + 8 > len(data):
        raise ValueError("Insufficient data for string length")
    str_len = struct.unpack_from("<Q", data, offset)[0]
    offset += 8
    if offset + str_len > len(data):
        raise ValueError("Insufficient data for string content")
    value = data[offset : offset + str_len].decode("utf-8", errors="replace")
    offset += str_len
    return value, offset


def _read_value(data: bytes, offset: int, value_type: int) -> tuple[object, int]:
    """Read a single GGUF value based on its type.

    Returns (value, new_offset).
    """
    if value_type == GGUF_TYPE_UINT8:
        val = struct.unpack_from("<B", data, offset)[0]
        return val, offset + 1
    elif value_type == GGUF_TYPE_INT8:
        val = struct.unpack_from("<b", data, offset)[0]
        return val, offset + 1
    elif value_type == GGUF_TYPE_UINT16:
        val = struct.unpack_from("<H", data, offset)[0]
        return val, offset + 2
    elif value_type == GGUF_TYPE_INT16:
        val = struct.unpack_from("<h", data, offset)[0]
        return val, offset + 2
    elif value_type == GGUF_TYPE_UINT32:
        val = struct.unpack_from("<I", data, offset)[0]
        return val, offset + 4
    elif value_type == GGUF_TYPE_INT32:
        val = struct.unpack_from("<i", data, offset)[0]
        return val, offset + 4
    elif value_type == GGUF_TYPE_FLOAT32:
        val = struct.unpack_from("<f", data, offset)[0]
        return val, offset + 4
    elif value_type == GGUF_TYPE_BOOL:
        val = struct.unpack_from("<B", data, offset)[0] != 0
        return val, offset + 1
    elif value_type == GGUF_TYPE_STRING:
        return _read_string(data, offset)
    elif value_type == GGUF_TYPE_UINT64:
        val = struct.unpack_from("<Q", data, offset)[0]
        return val, offset + 8
    elif value_type == GGUF_TYPE_INT64:
        val = struct.unpack_from("<q", data, offset)[0]
        return val, offset + 8
    elif value_type == GGUF_TYPE_FLOAT64:
        val = struct.unpack_from("<d", data, offset)[0]
        return val, offset + 8
    elif value_type == GGUF_TYPE_ARRAY:
        # Array: elem_type (uint32), count (uint64), then count elements
        if offset + 12 > len(data):
            raise ValueError("Insufficient data for array header")
        elem_type = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        count = struct.unpack_from("<Q", data, offset)[0]
        offset += 8
        # Read array elements (but we only need the first for metadata)
        values = []
        for _ in range(min(count, 256)):  # Safety limit
            val, offset = _read_value(data, offset, elem_type)
            values.append(val)
        # Skip remaining elements if count > 256
        return values, offset
    else:
        raise ValueError(f"Unknown GGUF value type: {value_type}")


def read_gguf_metadata(model_path: str | Path) -> dict:
    """Read metadata from a GGUF model file.

    Extracts architecture information such as layer count, embedding dimension,
    head count, context length, and architecture name. Uses only Python stdlib.

    If the file doesn't exist, isn't a valid GGUF file, or parsing fails,
    returns safe defaults with parse_success=False.

    Args:
        model_path: Path to the GGUF model file (str or Path).

    Returns:
        dict with keys:
            file_size_bytes (int): Size of the model file in bytes.
            n_layer (int): Number of attention layers.
            n_embd (int): Embedding dimension.
            n_head (int): Number of attention heads.
            context_length (int): Maximum context length.
            architecture (str): Model architecture name.
            parse_success (bool): Whether GGUF parsing succeeded.
    """
    path = Path(model_path)

    # File existence check
    if not path.exists():
        return dict(_DEFAULTS)

    try:
        file_size = path.stat().st_size
    except OSError:
        return dict(_DEFAULTS)

    if file_size < 16:
        # Too small to be a valid GGUF file
        return {**_DEFAULTS, "file_size_bytes": file_size}

    try:
        with open(path, "rb") as f:
            # Read header: magic (4) + version (4) + tensor_count (8) + metadata_kv_count (8)
            # GGUFv2 and v3 have the same header layout for our purposes
            header_size = 24
            header = f.read(header_size)
            if len(header) < header_size:
                return {**_DEFAULTS, "file_size_bytes": file_size}

            # Check magic
            magic = header[0:4]
            if magic != b"GGUF":
                return {**_DEFAULTS, "file_size_bytes": file_size}

            version = struct.unpack_from("<I", header, 4)[0]
            if version < 2 or version > 3:
                return {**_DEFAULTS, "file_size_bytes": file_size}

            tensor_count = struct.unpack_from("<Q", header, 8)[0]  # noqa: F841
            metadata_kv_count = struct.unpack_from("<Q", header, 16)[0]

            # Now read metadata KV pairs
            # We need to scan through the key-value pairs to find the ones we want.
            # Read a chunk of data to parse metadata from (up to 1 MB should be plenty)
            max_meta_read = min(file_size - header_size, 1 * 1024 * 1024)
            f.seek(header_size)
            meta_data = f.read(max_meta_read)

            result: dict = {
                "file_size_bytes": file_size,
                "n_layer": 32,
                "n_embd": 3200,
                "n_head": 32,
                "context_length": 4096,
                "architecture": "unknown",
                "parse_success": False,
            }

            offset = 0
            found_keys: set[str] = set()
            target_keys = set(_METADATA_KEYS.keys())

            for _ in range(metadata_kv_count):
                if offset + 8 > len(meta_data):
                    break  # Ran out of data

                # Read key
                key, offset = _read_string(meta_data, offset)

                # Read value type
                if offset + 4 > len(meta_data):
                    break
                value_type = struct.unpack_from("<I", meta_data, offset)[0]
                offset += 4

                # Read value
                value, offset = _read_value(meta_data, offset, value_type)

                # Check if this is a key we care about
                if key in target_keys:
                    field_name = _METADATA_KEYS[key]
                    if field_name == "architecture":
                        result[field_name] = str(value)
                    else:
                        # Numeric fields
                        with contextlib.suppress(ValueError, TypeError):
                            result[field_name] = int(value)
                    found_keys.add(key)

                # Early exit if we found all keys
                if found_keys == target_keys:
                    break

                # Safety: if offset is past our buffer, stop
                if offset >= len(meta_data):
                    break

            result["parse_success"] = len(found_keys) > 0
            return result

    except (OSError, struct.error, ValueError, UnicodeDecodeError):
        # Any parsing error → return defaults
        return {**_DEFAULTS, "file_size_bytes": file_size}
