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
        self.array = None

    def open_image_as_array(self, path):
        if not self.array:
            try:
                with PILImage.open(path) as img:
                    self.array = np.array(img)
                    self.width, self.height = img.size
                return self.array
            except FileNotFoundError:
                raise FileNotFoundError(f"Immagine non trovata: {path}")
            except Exception as e:
                raise Exception(f"Errore durante il caricamento dell'immagine: {e}")
        else:
            raise Exception("Immagine già caricata")

    def save(self, data, path, ext):
        try:
            PILImage.fromarray(data).save(Image._png_path(path), ext)
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