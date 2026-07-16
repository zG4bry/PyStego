from PIL import Image
import numpy as np
from enum import IntEnum
import struct
import src.utils.utils as utils


class EncodingLevel(IntEnum):
    LOW = 0
    MED = 1
    HIGH = 2


_BITS_PER_VALUE = {
    EncodingLevel.LOW: 1,
    EncodingLevel.MED: 2,
    EncodingLevel.HIGH: 4,
}


class Encoder:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.image = None
        self.array = None

    @staticmethod
    def encode(image: Image.Image, secret, level: EncodingLevel):
        secret_array = Encoder._to_array(secret)
        bits_per_value = _BITS_PER_VALUE[level]
        values_per_byte = 8 // bits_per_value
        mask = np.uint8((1 << bits_per_value) - 1)

        # Header: lunghezza del segreto in byte (big-endian, 4 byte)
        header = struct.pack(">I", len(secret_array))
        payload = np.frombuffer(header + secret_array.tobytes(), dtype=np.uint8)

        image_flat = np.array(image.convert("RGBA"), dtype=np.uint8).reshape(-1)

        required_values = len(payload) * values_per_byte
        if required_values > image_flat.size:
            raise ValueError(
                "L'immagine di copertura è troppo piccola per nascondere il segreto "
                f"(necessari {required_values} valori, disponibili {image_flat.size})"
            )

        idx = 0
        for byte in payload:
            byte = int(byte)
            for pos in range(values_per_byte):
                nibble = (byte >> (pos * bits_per_value)) & mask
                image_flat[idx] = (image_flat[idx] & ~mask) | nibble
                idx += 1

        return image_flat

    @staticmethod
    def encoded_size(size, level: EncodingLevel):
        bits_per_value = _BITS_PER_VALUE[level]
        return size * (8 // bits_per_value)

    @staticmethod
    def decode(image: Image.Image, level: EncodingLevel):
        # TODO: implementare l'estrazione leggendo l'header di lunghezza
        pass

    @staticmethod
    def _to_array(secret):
        if isinstance(secret, str):
            secret = utils.text_to_array(secret)
        elif isinstance(secret, Image.Image):
            secret = utils.img_to_array(secret)
        else:
            raise TypeError("L'argomento deve essere una stringa o un'immagine PIL")
        return secret
