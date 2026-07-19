# Piano — Anteprime immagini + SSIM reale

Data: 2026-07-17

## Contesto

La GUI attuale mostra solo i **path testuali** delle immagini (nessuna
anteprima) e l'SSIM è un valore **finto** hardcoded (`"SSIM: 0.99 (Simulato)"`),
mai calcolato. `encode()` restituisce un array RGBA piatto (non un `PIL.Image`).

Stato dipendenze nel venv (Python 3.14):
- Presenti: `numpy`, `Pillow`, `customtkinter` (con `CTkImage`), `pytest`.
- Assenti: `scikit-image`, `scipy`.
- `scikit-image 0.26.0` è disponibile per Python 3.14 (traina `scipy`,
  `imageio`, `networkx`, `tifffile`, `lazy-loader`).

## Decisioni concordate con l'utente

- **SSIM**: usare `skimage.metrics.structural_similarity` (scikit-image).
- **Layout GUI**: anteprime affiancate prima/dopo (encode) + anteprime nel decode.
- **Anteprima risultato encode**: subito dopo `encode`, prima del salvataggio.
- **Decode**: anteprime anche nella schermata di decodifica.

## Piano

### Fase 0 — Dipendenze
- `requirements.txt`: aggiungere `scikit-image` (traina `scipy`, `imageio`, ecc.).
- Verifica in esecuzione: `venv/bin/pip install scikit-image` e import
  `from skimage.metrics import structural_similarity`.
- Fallback: se `scipy`/`scikit-image` non si installano su Python 3.14,
  ripiegare su implementazione SSIM numpy-only con la **stessa API**
  (`metrics.ssim`), così GUI e test non cambiano.

### Fase 1 — Modulo metriche (`src/core/metrics.py`, nuovo)
- `ssim(img_a, img_b) -> float`: accetta due `PIL.Image` (o array), normalizza a
  RGB, chiama `structural_similarity(a, b, channel_axis=-1, data_range=255)`.
  Ritorna un float 0–1.
- Se le due immagini hanno dimensioni diverse → `ValueError`.
- Motivazione: metrica fuori da GUI ed encoder (separazione responsabilità,
  testabile).

### Fase 2 — Helper immagine condivisi (`src/utils/utils.py`)
- `flat_to_image(data, width, height) -> PIL.Image`: ricostruisce un `PIL.Image`
  RGBA/RGB dall'array piatto prodotto da `encode()` (estrae la logica di reshape
  oggi dentro `save`, che verrà rifattorizzato per riusarla).
- `make_thumbnail(img, max_side=260) -> PIL.Image`: copia ridimensionata per
  l'anteprima, senza alterare l'originale.
- Motivazione: mostrare l'anteprima del risultato **prima** di salvare, senza
  passare dal disco.

### Fase 3 — Componente anteprima riutilizzabile (`src/gui/image_preview.py`, nuovo)
- `ImagePreview(ctk.CTkFrame)`: widget con titolo (es. "Originale"/"Risultato")
  e una `CTkLabel` che ospita una `ctk.CTkImage`. Metodi `show(pil_image)` e
  `clear()`.
- Mantiene un riferimento alla `CTkImage` per evitare il garbage-collection
  (bug classico Tk).
- Motivazione: stesso componente riusato in encode (2×) e decode (2×).

### Fase 4 — Refactor `EncodeFrame`
Layout per ogni tab (testo e immagine), a griglia:
- Riga controlli: selezione cover, (tab immagine) selezione segreto, selezione
  livello, bottone "Codifica".
- Riga anteprime: `ImagePreview("Copertura")` a sinistra,
  `ImagePreview("Risultato")` a destra.
- Riga esito: label con path salvataggio + **SSIM reale**.

Comportamento:
- Selezione cover → mostra subito l'anteprima "Copertura".
- Click "Codifica": esegue `encode`, ricostruisce l'immagine con
  `utils.flat_to_image`, mostra l'anteprima "Risultato", calcola
  `metrics.ssim(cover, risultato)` e aggiorna la label. **Poi** propone il
  salvataggio (separato, opzionale).
- Errori (`ValueError` capienza) mostrati nella label esito, niente crash.

### Fase 5 — Refactor `DecodeFrame`
- Tab "Estrai Testo": anteprima della **stego caricata** + textbox risultato.
- Tab "Estrai Immagine": anteprima **stego caricata** a sinistra, anteprima
  **immagine estratta** a destra; salvataggio opzionale dopo l'estrazione.
- Selezione stego → mostra anteprima. Decode immagine → mostra il segreto
  estratto prima di salvare.

### Fase 6 — Ritocchi finestra (`src/gui/app.py`)
- Aumentare dimensione minima/predefinita finestra (es. 900×640) per contenere
  le due anteprime affiancate.
- Verificare i `grid` weights per il ridimensionamento corretto.

### Fase 7 — Test (`tests/`)
- `tests/test_metrics.py`:
  - `ssim(img, img) == 1.0` (immagine identica).
  - `ssim` tra cover e stego LSB alto (> 0.98 a LOW).
  - immagini di dimensioni diverse → `ValueError`.
- Estensione test utils: `flat_to_image` round-trip con `encode`/reshape.
- GUI non testata automaticamente (serve display); verifica import headless
  (`python -c "import src.gui.app"`).

### Fase 8 — Docs
- `README.md` / `AGENTS.md`: nuova dipendenza `scikit-image`, nuovo modulo
  `metrics.py`, componente `ImagePreview`, SSIM ora reale.

## Rischi / punti aperti

1. **`scipy` su Python 3.14**: se l'install fallisce, ripiego su SSIM numpy-only
   (stessa API `metrics.ssim`).
2. **Anteprima `CTkImage` GC**: gestita tenendo il riferimento nel widget.
3. **Immagini grandi**: uso thumbnail per l'anteprima; l'originale resta intatto
   per encode/save.

## File toccati/creati

- Nuovi: `src/core/metrics.py`, `src/gui/image_preview.py`,
  `tests/test_metrics.py`.
- Modificati: `src/gui/encode_frame.py`, `src/gui/decode_frame.py`,
  `src/gui/app.py`, `src/utils/utils.py`, `requirements.txt`, `README.md`,
  `AGENTS.md` (+ possibile estensione test utils).

## Ordine di esecuzione

0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

Ogni fase mantiene il progetto eseguibile (`python -m src.main` da repo root).
