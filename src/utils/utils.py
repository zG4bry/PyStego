from PIL import Image
import numpy as np
from pathlib import Path

def load(path):
    try:
        with Image.open(path).convert("RGBA") as img:
            image = img
            return image
    except FileNotFoundError:
        raise FileNotFoundError(f"Immagine non trovata: {path}")
    except Exception as e:
        raise Exception(f"Errore durante il caricamento dell'immagine: {e}")

def text_to_array(data: str):
    if isinstance(data, str):
        data = data.encode("utf-8")
    else:
        raise TypeError("L'argomento deve essere una stringa")
    return np.frombuffer(data, dtype=np.uint8)

def img_to_array(img: Image.Image):
    if isinstance(img, Image.Image):
        return np.array(img, dtype=np.uint8).flatten()
    else:
        raise TypeError("L'argomento deve essere un'immagine PIL")
    
def save(data: Image.Image, width: int, height: int, path, ext):
    try:
        img_array = data.reshape(height, width, 4)
        Image.fromarray(img_array).save(png_path(path), ext)
        return True
    except Exception as e:
        raise Exception(f"Errore durante il salvataggio dell'immagine: {e}")

def png_path(path):
    if Path(path).suffix != ".png":
        path = str(Path(path).with_suffix(".png"))
    return path
