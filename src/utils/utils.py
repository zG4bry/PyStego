from pathlib import Path
import numpy as np
from PIL import Image, UnidentifiedImageError


def load(path):
    try:
        with Image.open(path).convert("RGBA") as img:
            return img
    except FileNotFoundError:
        raise FileNotFoundError(f"Immagine non trovata: {path}")
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError(f"Errore durante il caricamento dell'immagine: {e}")


def text_to_array(data: str) -> np.ndarray:
    if isinstance(data, str):
        data = data.encode("utf-8")
    else:
        raise TypeError("L'argomento deve essere una stringa")
    return np.frombuffer(data, dtype=np.uint8)


def img_to_array(img: Image.Image) -> np.ndarray:
    if isinstance(img, Image.Image):
        return np.array(img, dtype=np.uint8).flatten()
    else:
        raise TypeError("L'argomento deve essere un'immagine PIL")


def image_to_flat_rgba(img: Image.Image) -> np.ndarray:
    return np.array(img.convert("RGBA"), dtype=np.uint8).ravel()


def flat_to_image(data: np.ndarray, width: int, height: int) -> Image.Image:
    """Ricostruisce un'immagine PIL dall'array numpy piatto prodotto dall'encoder."""
    channels = data.size // (width * height)
    img_array = data.reshape(height, width, channels)
    return Image.fromarray(img_array, "RGBA" if channels == 4 else "RGB")


def make_thumbnail(img: Image.Image, max_side: int = 260) -> Image.Image:
    """Crea una miniatura per l'anteprima, preservando l'aspect ratio."""
    thumb = img.copy()
    thumb.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return thumb


def save(data: np.ndarray, width: int, height: int, path, ext: str = "png"):
    try:
        img = flat_to_image(data, width, height)
        img.save(png_path(path), ext.upper())
    except (OSError, ValueError) as e:
        raise ValueError(f"Errore durante il salvataggio dell'immagine: {e}")


def png_path(path):
    if Path(path).suffix != ".png":
        path = str(Path(path).with_suffix(".png"))
    return path


def to_array(secret) -> np.ndarray:
    if isinstance(secret, str):
        secret = text_to_array(secret)
    elif isinstance(secret, Image.Image):
        secret = img_to_array(secret)
    else:
        raise TypeError("L'argomento deve essere una stringa o un'immagine PIL")
    return secret
