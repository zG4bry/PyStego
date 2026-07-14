from PIL import Image as PILImage
import numpy as np

class EncodingLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Image:
    def __init__(self):
        self.widht = 0
        self.height = 0
        self.image = None
    
    def load(path):
        pass

    def save(path):
        pass

    def encode(data, level: EncodingLevel):
        pass

    def decode(level: EncodingLevel):
        pass
        return data
