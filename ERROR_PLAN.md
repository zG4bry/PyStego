# Piano degli errori — PyStego

Data: 2026-07-19
Verificato leggendo `src/core/encoder.py`, `src/utils/utils.py`, `tests/test_encoder.py` e
mandando round-trip reali. Tutti i punti sotto sono stati riprodotti, non speculativi.

Riferimenti: `AGENTS.md` (contratto encoder), `REFACTOR_PLAN.md` (problemi noti 4, 6, 7, 8).

---

## ~~BUG 1 — Segreti-immagine non quadrati vengono trasposti~~ — RISOLTO (2026-07-19)

**Stato:** l'inversione `height, width = secret.size` è stata corretta in
`src/core/encoder.py:107` (`width, height = secret.size`). Verificato round-trip con
segreto rettangolare `20x10` a tutti i livelli LOW/MED/HIGH: `np.array_equal` OK.

**Perché succedeva:** `secret.size` di PIL è `(width, height)`; assegnandolo a
`height, width` lo `shape` salvato nel payload diventava `(H, W, 3)`, e `decode`
(`encoder.py:169-172`) ricostruiva l'immagine trasposta. Le immagini quadrate dei test
mascheravano il bug.

**Azione residua:** aggiungere comunque un test rettangolare in `tests/test_encoder.py`
(`Image.new("RGB", (40, 10))` a tutti i livelli) per evitare regressioni.

---

## BUG 2 — `TypeError` non gestito dalla GUI per segreto non valido (MEDIO)

**Dove:** `src/core/encoder.py:103` chiama `utils.to_array(secret)` che solleva `TypeError`
(`utils/utils.py:61`) se `secret` non è `str` né `PIL.Image`.

**Problema:** `encode` documenta di sollevare `ValueError` (vedi `AGENTS.md` e la gestione
`except ValueError` in `encode_frame.py:148` e `decode_frame.py:116`). Ma un segreto di tipo
sconosciuto produce `TypeError`, che **non** viene catturato dai `try/except ValueError` della
GUI → crash della finestra invece di un messaggio in label.

**Soluzione (scelta A, minima):** in `encode`/`decode` intercettare e rilanciare come
`ValueError`:
```python
try:
    secret_array = utils.to_array(secret)
except TypeError as e:
    raise ValueError(str(e))
```
Oppure (scelta B) allargare i `except` della GUI a `(ValueError, TypeError)`. La A è
preferibile perché mantiene il contratto "solo ValueError" documentato in `AGENTS.md`.

---

## ROBUSTEZZA 3 — `utils.load` cattura `Exception` troppo generico (BASSO, noto)

**Dove:** `src/utils/utils.py:14-15`

```python
except Exception as e:
    raise ValueError(f"Errore durante il caricamento dell'immagine: {e}")
```

Già segnalato in `REFACTOR_PLAN.md` problema 8. Maschera errori inattesi (es. `MemoryError`,
`KeyboardInterrupt`) trasformandoli in `ValueError` "caricamento". Mitigato dal fatto che gli
errori reali di PIL (`FileNotFoundError`, `UnidentifiedImageError`) sono già gestiti prima.
**Azione:** restringere a `(UnidentifiedImageError, OSError)` invece di `Exception`.

---

## ROBUSTEZZA 4 — `utils.save` cattura `Exception` e ritorna `True`/`raise` (BASSO)

**Dove:** `src/utils/utils.py:37-46`

```python
def save(...):
    try:
        ...
        return True
    except Exception as e:
        raise ValueError(...)
```

- Cattura `Exception` generico (come sopra).
- La GUI (`encode_frame.py`, `decode_frame.py`) **non controlla** il valore di ritorno
  `True`/nessuno, quindi un fallimento silenzioso non esiste (perché fa `raise`), ma il
  valore di ritorno è inutile e fuorviante.
- Il type-hint/doc (problema 7 di `REFACTOR_PLAN.md`) diceva `data: Image.Image` ma riceve
  un array numpy — ora già corretto nel codice, solo da confermare nel docstring.

**Azione:** restringere l'`except` a `(OSError, ValueError)` e rimuovere il `return True`
(inutile) o documentarlo; aggiornare il docstring se presente.

---

## DEBT 5 — Log in console invece di feedback UI (BASSO, noto)

**Dove:** `encode_frame.py:166` e `decode_frame.py:133` usano `print(...)` per confermare il
salvataggio. L'utente della GUI non vede il terminale.

**Azione:** mostrare il path salvato in una `CTkLabel` di stato (come già fa
`lbl_status_img` in decode), nello stesso stile delle altre label di errore.

---

## Ordine di intervento consigliato

1. **BUG 2** (gestione `TypeError` -> `ValueError`) — evita crash GUI. ~1 riga + test.
2. **ROBUSTEZZA 3 / 4** — restringere `except`, pulizia `save`.
3. **DEBT 5** — `print` -> label di stato.
4. **Test rettangolare** (azione residua BUG 1) — aggiungere in `tests/test_encoder.py`.

Dopo le modifiche, eseguire `venv/bin/python -m pytest tests/` (dal repo root) per
confermare che i nuovi test passino e quelli esistenti restino verdi.
