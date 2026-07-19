# AGENTS.md

PyStego: a steganography GUI (hide text/images inside images) built with customtkinter. Code, comments, and UI strings are in Italian — keep that convention.

## Run the app
- Run only as a module from the repo root: `venv/bin/python -m src.main`.
- `src/` uses **relative imports** internally; the only supported way to launch is `python -m src.main` from the repo root. Do NOT reintroduce `from src...` imports in app code.
- It is a Tk GUI needing a display (X/Wayland); it will not start in a headless environment.

## Tests
- Run from the repo root: `venv/bin/python -m pytest tests/`.
- The test file uses **absolute** imports (`from src.core.encoder import ...`), so it relies on the repo root being on `sys.path` (i.e. run from root). This differs from the app's relative-import convention — keep both intact.
- Tests use temp files under `/tmp`; no fixtures, services, or network required.

## Dependencies
- `requirements.txt` pins `customtkinter`, `numpy`, `pillow`, `pytest`. Install with `venv/bin/pip install -r requirements.txt`.
- `venv/` is Python 3.14 and gitignored. Pillow's C extension previously failed to import under 3.14 (`cannot import name 'Image' from 'PIL'`); a force-reinstall of pillow fixed it. If it breaks again: `venv/bin/pip install --force-reinstall --no-deps pillow`.

## Architecture
- Entrypoint: `src/main.py` -> `src/gui/app.py` (`App`, a `ctk.CTk`) -> sidebar + `EncodeFrame` / `DecodeFrame`.
- `src/core/encoder.py`: steganography as **module-level functions** (`encode`, `decode`, `required_channels`, `EncodingLevel`). `EncodingLevel` LOW/MED/HIGH = 1/2/4 bits per channel.
- `src/utils/utils.py`: image load/save and text/image <-> array conversion. `save(data, w, h, path, ext)` receives a **flat numpy array** (not a PIL image) and reshapes it to `(h, w, ch)`; for `ch==4` it writes RGBA, else RGB. `image_to_flat_rgba` always converts to RGBA.

## Encoder contract (easy to get wrong)
- `encode(img, secret, level)` returns the modified **flat 1D RGBA uint8 array** (length `H*W*4`). Callers reshape to `(H, W, 4)` and persist via `utils.save(data, w, h, path, "png")`.
- Payload layout in the image: `[4-byte big-endian length][1-byte type][secret]`; type `0` = text, `1` = image. For image secrets, `encode` also embeds `(width, height, channels)` as 3×2-byte big-endian before the pixels so `decode` can reconstruct the original. Keep `encode`/`decode` in sync via the shared `_pack_header`/`_unpack_header` helpers.
- Bits are embedded **only in RGB channels** (alpha is never touched), so transparent covers are preserved. Covers are forced to RGBA inside `image_to_flat_rgba`.
- `decode(img, level)` returns `(kind, data)`: `("text", str)` or `("image", PIL.Image.Image)`. It raises `ValueError` on missing/invalid secret or wrong level — the GUI must catch these and show them in a label.
