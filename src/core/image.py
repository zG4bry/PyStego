from PIL import Image as PILImage
from pathlib import Path
import numpy as np
from enum import IntEnum

class EncodingLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Image:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.image = None

    def load(self, path: str) -> bool:
        if not self.image:
            try:
                with PILImage.open(path).convert("RGBA") as img:
                    self.image = np.array(img, dtype=np.uint8).ravel()
                    self.width, self.height = img.size
                return True
            except FileNotFoundError:
                raise FileNotFoundError(f"Immagine non trovata: {path}")
            except Exception as e:
                raise Exception(f"Errore durante il caricamento dell'immagine: {e}")
        else:
            print("Immagine già caricata")
            return False

    def save(self, data, path, ext):
        if self.image is None:
            return False
        try:
            img_array = data.reshape(self.height, self.width, 4)
            PILImage.fromarray(img_array).save(Image._png_path(path), ext)
            return True
        except Exception as e:
            raise Exception(f"Errore durante il salvataggio dell'immagine: {e}")

    def encode(self, data, level: EncodingLevel):
        pass

    def decode(level: EncodingLevel):
        pass

    @staticmethod
    def _png_path(path):
        if Path(path).suffix != ".png":
            path = str(Path(path).with_suffix(".png"))
        return path
    