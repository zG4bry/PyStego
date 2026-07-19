# PyStego

Steganografia GUI: nascondi testo o immagini all'interno di altre immagini,
scritta con customtkinter.

## Avvio

```bash
venv/bin/python -m src.main
```

Eseguire sempre dal root del repo. È una GUI Tk, quindi serve un display
(X/Wayland); in ambiente headless non parte.

## Dipendenze

```bash
venv/bin/pip install -r requirements.txt
```
Il progetto ora usa anche `scikit-image` per calcolare il vero valore SSIM delle immagini.

## Funzionamento

- `src/core/encoder.py`: motore di steganografia (`encode`/`decode`,
  `EncodingLevel` LOW/MED/HIGH = 1/2/4 bit per canale). Lavora solo sui canali
  RGB (l'alpha resta intatto).
- Il payload nel file è: `[4B lunghezza big-endian][1B tipo][segreto]`.
  Tipo `0` = testo, `1` = immagine; per i segreti-immagine seguono
  `width`, `height`, `channels` (3×2 byte big-endian).
- `src/gui/`: `app.py` (finestra + cambio viste), `sidebar.py`,
  `encode_frame.py`, `decode_frame.py`. Entrambi i frame permettono di
  scegliere il livello di codifica/decodifica.

## Test

```bash
venv/bin/python -m pytest tests/
```
