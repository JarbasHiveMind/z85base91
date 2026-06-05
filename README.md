# z85base91

Compact binary-to-text encoding library providing three codecs — **Base91**, **Z85B**, and **Z85P** — for efficient serialisation of binary payloads over text-oriented channels. Combines fast C implementations with pure-Python fallbacks for cross-platform compatibility. Packaged for the HiveMind mesh.

## Why z85base91?

Base64 expands data by 33% (1.33x), but **Base91 achieves only 23% overhead** (1.23x expansion) while remaining more compact than base32 (62% overhead). Z85 variants (Z85B: 1.25x, Z85P: 1.28x) offer a middle ground with character safety guarantees useful for serialising encrypted frames over websockets and other text transports.

### Comparison

| Codec | Expansion | Use Case |
|-------|-----------|----------|
| **Base91** | 1.23x (smallest) | Maximum compactness; printable ASCII |
| **Z85B** | 1.25x | Z85 padding scheme; per-group framing |
| **Z85P** | 1.28x | Z85 padding scheme; prepended size byte |
| base64 | 1.35x | Standard; less compact |
| base32 | 1.62x | Case-insensitive; largest |

## Installation

```bash
pip install z85base91
```

The library bundles precompiled C extensions for x86_64, i386, and aarch64 architectures. It automatically falls back to pure Python if the C library fails to load, with a logged warning.

## Quick Start

```python
from z85base91 import B91, Z85B, Z85P

# Base91 (most compact)
data = b"Hello, World!"
encoded = B91.encode(data)        # b'>OwJh>}AQ;r@@Y?F'
decoded = B91.decode(encoded)     # b'Hello, World!'

# Z85B (Z85 with independent groups)
encoded = Z85B.encode(data)
decoded = Z85B.decode(encoded)

# Z85P (Z85 with prepended padding byte)
encoded = Z85P.encode(data)
decoded = Z85P.decode(encoded)
```

All three accept `str` or `bytes` input and return `bytes`.

## Public API

### Base91 — `B91`

```python
from z85base91 import B91
```

**Encoding**

```python
B91.encode(data: Union[str, bytes], encoding: str = "utf-8") -> bytes
```

Encodes binary data using Base91, which uses 91 printable ASCII characters (A–Z, a–z, 0–9, plus 27 symbols). Achieves 1.23x size expansion.

**Arguments:**
- `data`: Input as `str` (encoded to UTF-8) or raw `bytes`.
- `encoding`: Character encoding if `data` is `str`. Default: `"utf-8"`.

**Returns:** Base91-encoded bytes.

**Example:**
```python
B91.encode(b"test")           # b'fPNKd'
B91.encode("test")            # b'fPNKd' (auto UTF-8)
B91.encode(b"\x00\x01\x02")   # b':CQA'
```

**Decoding**

```python
B91.decode(encoded_data: Union[str, bytes], encoding: str = "utf-8") -> bytes
```

Decodes Base91-encoded input back to raw bytes.

**Arguments:**
- `encoded_data`: Base91 string or bytes.
- `encoding`: Character encoding to use for string conversion. Default: `"utf-8"`.

**Returns:** Decoded bytes.

**Raises:** `ValueError` if the input contains invalid Base91 characters (outside the 91-character alphabet).

**Example:**
```python
B91.decode(b'>OwJh>}AQ;r@@Y?F')  # b'Hello, World!'
B91.decode('>OwJh>}AQ;r@@Y?F')   # b'Hello, World!' (str input)
```

---

### Z85B — `Z85B`

```python
from z85base91 import Z85B
```

**Encoding**

```python
Z85B.encode(data: Union[str, bytes]) -> bytes
```

Encodes binary data using Z85B, a variant of Z85 that processes 4-byte chunks independently. Uses the 85-character Z85 alphabet: `0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#`. Achieves ~1.25x expansion.

**Arguments:**
- `data`: Input as `str` (encoded to UTF-8) or raw `bytes`.

**Returns:** Z85B-encoded bytes.

**Example:**
```python
Z85B.encode(b"Hello")         # b'NV0&yq1' (5 bytes -> 7 bytes)
Z85B.encode("Hello")          # b'NV0&yq1' (str auto UTF-8)
```

**Decoding**

```python
Z85B.decode(encoded_data: Union[str, bytes]) -> bytes
```

Decodes Z85B-encoded input.

**Arguments:**
- `encoded_data`: Z85B-encoded string or bytes.

**Returns:** Decoded bytes.

**Raises:** `ValueError` if input contains invalid Z85 characters.

**Example:**
```python
original = b"Hello, World!"
encoded = Z85B.encode(original)
decoded = Z85B.decode(encoded)
assert decoded == original
```

---

### Z85P — `Z85P`

```python
from z85base91 import Z85P
```

**Encoding**

```python
Z85P.encode(data: Union[str, bytes]) -> bytes
```

Encodes binary data using Z85P, a Z85 variant with an **explicit padding byte** prepended. The first byte of the output indicates how many padding bytes were added (0–3), allowing the decoder to strip them correctly. Uses the same 85-character Z85 alphabet as Z85B. Achieves ~1.28x expansion.

**Arguments:**
- `data`: Input as `str` (encoded to UTF-8) or raw `bytes`.

**Returns:** Z85P-encoded bytes (first byte is padding indicator, 0–3).

**Example:**
```python
Z85P.encode(b"A")      # b'\x03k(Z(+' (1 byte + 3 padding = 4, encodes to 5)
Z85P.encode(b"AB")     # b'\x02k%+LK' (2 bytes + 2 padding = 4)
Z85P.encode(b"ABCD")   # b'\x00k%^}b' (4 bytes, no padding)
```

**Decoding**

```python
Z85P.decode(encoded_data: Union[str, bytes]) -> bytes
```

Decodes Z85P-encoded input, automatically stripping padding based on the first byte.

**Arguments:**
- `encoded_data`: Z85P-encoded string or bytes (must include the padding indicator byte).

**Returns:** Decoded bytes with padding removed.

**Raises:** `ValueError` if input length is invalid or contains invalid Z85 characters.

**Example:**
```python
original = b"X"
encoded = Z85P.encode(original)
decoded = Z85P.decode(encoded)
assert decoded == original
```

---

## Performance Notes

### C vs. Python

The C implementations are substantially faster (~1.5x for decoding, up to 2x for encoding). The library automatically selects the C path; Python fallback engages only if compilation failed or the C library failed to load.

The package ships a benchmark harness (`z85base91/bench.py`) that compares all
codecs against stdlib `base64`/`base32` across input sizes. It pulls in
`click`, `tabulate`, `pybase64`, and `hivemind-bus-client` (for the pure-Python
reference codecs), so install those before running:

```bash
pip install click tabulate pybase64 hivemind-bus-client
python -m z85base91.bench
```

Expansion ratios are deterministic: Base91 ≈ 1.23x, Z85B ≈ 1.25x, Z85P ≈ 1.25x
for aligned payloads (up to 1.28x for short, heavily-padded inputs), versus
base64's 1.33x and base32's 1.6x. Absolute throughput depends on hardware; the
C path is consistently faster than stdlib `base64` for encoding and the pure
Python fallback for both directions.

---

## Architecture

The library has three layers:

1. **Public API** (`z85base91/__init__.py`): Exports `B91`, `Z85B`, `Z85P` classes. At import time, each tries to load its architecture-specific C library (`.so`) via `ctypes.CDLL`. If loading fails, the name is rebound to the pure-Python implementation.

2. **C implementations** (`src/*.c`, prebuilt as `z85base91/lib*-{arch}.so`):
   - `libbase91-{x86_64,aarch64,i386}.so` — B91 codec
   - `libz85b-{x86_64,aarch64,i386}.so` — Z85B codec
   - `libz85p-{x86_64,aarch64,i386}.so` — Z85P codec

3. **Pure-Python fallbacks** (`z85base91/{b91,z85b,z85p}.py`): Self-contained reference implementations.

Data flow: normalise input to bytes → wrap in `ctypes.c_ubyte` array → call C function → read output via `ctypes.string_at`.

---

## Error Handling

**Invalid input characters**

All decoders raise `ValueError` if the input contains characters outside the allowed alphabet:

```python
try:
    Z85P.decode("Hello🎉World")
except ValueError as e:
    print(f"Invalid character: {e}")
```

**Missing C library**

If the C library fails to load, a `WARNING` is logged and the Python fallback is used transparently:

```
WARNING - Z85P C library not available: Library load error. Falling back to pure Python implementation.
```

No exception is raised; encoding/decoding work identically, just slower.

---

## HiveMind Integration

This library is used by the HiveMind mesh to efficiently pack binary payloads (encrypted frames, keys, metadata) for transmission over websocket channels, where text-mode framing is required. The ~23% overhead (Base91) versus 33% (base64) yields measurable bandwidth savings at scale.

Example: a 1 MB encrypted message expands to 1.23 MB (Base91) versus 1.35 MB (base64) — a 12 KB/message saving that compounds with thousands of mesh nodes.

---

## Requirements

**Runtime:** Python 3.8+ (no external dependencies; `ctypes` is stdlib)

**Build:** `python3-dev`, `swig` (for C extension compilation)

**Tests:** `pytest~=7.1`, `pytest-cov~=4.1`

---

## Testing

```bash
pip install -e . --no-deps
pip install -r test/requirements.txt
pytest test/ -q
```

All codecs are tested for:
- Round-trip encode/decode (identity)
- Edge cases (empty input, single byte, odd lengths)
- Invalid input handling
- Unicode string support
- Large payloads (1000+ bytes)

---

## License

Apache 2.0
