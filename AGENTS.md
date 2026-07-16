# AGENTS.md

PyStego: a steganography GUI (hide text/images inside images) built with customtkinter.

## Running the app
- Run from the repo root as a module: `python -m src.main` (use `venv/bin/python`).
- Do NOT run `python src/main.py` or run from inside `src/`. Imports are inconsistent: `main.py`/`app.py`/`sidebar.py` use relative imports (`from .gui.app import App`) while `encode_frame.py`/`encoder.py` use absolute `src.`-prefixed imports (`from src.core.encoder import ...`). Only `python -m src.main` from the repo root resolves both.
- It is a Tk GUI, so it needs a display. In a headless environment it will fail to start (no X/Wayland display).

## Dependencies
- `requirements.txt` lists only `customtkinter==6.0.0`, but the code also imports `PIL` (Pillow) and `numpy`. The `venv/` has all three plus `darkdetect`/`packaging`.
- `venv/` is Python 3.14 and gitignored. Pillow's C extension previously failed to import under 3.14 (`cannot import name 'Image' from 'PIL'`); a `--force-reinstall` of `pillow` fixed it and it now imports. If it breaks again, reinstall: `venv/bin/pip install --force-reinstall --no-deps pillow`.

## Architecture
- `src/` is a package. Entrypoint: `src/main.py` -> `gui/app.py` (`App`, a `ctk.CTk`).
- `gui/`: `app.py` (window + frame switching), `sidebar.py`, `encode_frame.py`, `decode_frame.py`.
- `core/encoder.py`: the steganography engine (`Encoder`, `EncodingLevel` LOW/MED/HIGH = 1/2/4 bits per pixel). Operates on flattened RGBA numpy arrays.
- `utils/utils.py`: image load/save and text/image <-> array conversion. `save()` enforces PNG output and reshapes to `(height, width, 4)`.

## Gotchas
- `Encoder.decode()` is a stub (`@staticmethod def decode(image, level): pass`); only encoding works. No decode UI either (`decode_frame.py` is a TODO stub).
- `encode()` is a `@staticmethod` returning the modified **flat 1D RGBA array** (length `H*W*4`). It flattens the cover with `.reshape(-1)`, so callers must reshape via `utils.save(data, w, h, path, ext)`.
- `encode()` prepends a **4-byte big-endian length header** to the secret; a matching `decode()` must read that header to know the payload length (not yet implemented).
- The encoding GUI always uses `EncodingLevel.LOW`; there is no UI control to select MED/HIGH.
- Code, comments, and UI strings are in Italian; keep that convention.
- No tests, CI, or lint/format/typecheck config exist in this repo.
