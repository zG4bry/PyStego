# PyStego

Strumento di steganografia LSB (Least Significant Bit) con interfaccia grafica. Permette di nascondere testo o immagini all'interno di un'immagine di copertura.

## Funzionalità

- **Codifica LSB** a 3 livelli (1, 2 o 4 bit per canale RGB)
- **Nascondere testo** o **immagini** in un'immagine di copertura
- **Interfaccia grafica** moderna (customtkinter)
- **Metrica SSIM** per valutare la qualità dell'immagine codificata
- **Preservazione del canale alpha**
- **Header binario** con lunghezza e tipo del segreto

## Struttura del progetto

```
PyStego/
├── src/
│   ├── main.py              # Entry point
│   ├── core/
│   │   ├── encoder.py       # Logica LSB encode/decode
│   │   └── metrics.py       # Calcolo SSIM
│   ├── gui/
│   │   ├── app.py           # Finestra principale
│   │   ├── sidebar.py       # Navigazione
│   │   ├── encode_frame.py  # Frame di codifica
│   │   ├── decode_frame.py  # Frame di decodifica
│   │   └── image_preview.py # Widget anteprima
│   └── utils/
│       └── utils.py         # Utilità per immagini
├── tests/
│   ├── test_encoder.py      # Test roundtrip
│   └── test_metrics.py      # Test metrica
└── requirements.txt
```

## Installazione

```bash
# Crea e attiva virtual environment
python -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

## Utilizzo

```bash
# Avvia l'applicazione
python -m src.main
```

### Codifica (Nascondere)

1. Seleziona un'immagine di copertura (PNG, JPG, BMP)
2. Scegli il livello di codifica (LOW/MED/HIGH)
3. Inserisci il testo da nascondere **oppure** seleziona un'immagine segreta
4. Clicca "Codifica" per generare l'anteprima
5. Clicca "Salva" per salvare l'immagine steganografata

### Decodifica (Estrarre)

1. Seleziona un'immagine steganografata
2. Seleziona lo stesso livello di codifica usato per nascondere
3. Clicca "Estrai"
4. Il segreto estratto apparirà (testo o immagine)

## Livelli di codifica

| Livello | Bit per canale | Canali per byte | Capacità |
|---------|----------------|-----------------|----------|
| LOW     | 1              | 8               | 12.5%    |
| MED     | 2              | 4               | 25%      |
| HIGH    | 4              | 2               | 50%      |

**Nota:** livelli più alti offrono maggiore capacità ma peggiore qualità visiva.

## Test

```bash
pytest
```

## Dipendenze

- `customtkinter` - GUI moderna
- `numpy` - Manipolazione array
- `pillow` - Gestione immagini
- `scikit-image` - Calcolo SSIM
- `pytest` - Framework di test
