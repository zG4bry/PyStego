from PIL import Image
import numpy as np
from enum import IntEnum
import struct

from ..utils import utils


class EncodingLevel(IntEnum):
    LOW = 0
    MED = 1
    HIGH = 2


_BITS_PER_CHANNEL = {
    EncodingLevel.LOW: 1,
    EncodingLevel.MED: 2,
    EncodingLevel.HIGH: 4,
}

# Costanti dell'header del payload
_HEADER_LEN_BYTES = 4  # lunghezza segreto in byte (big-endian)
_HEADER_TYPE_BYTES = 1  # 0 = testo, 1 = immagine
_HEADER_SHAPE_BYTES = 6  # per immagini: width(2) + height(2) + channels(2), big-endian
_TYPE_TEXT = 0
_TYPE_IMAGE = 1


def _params(level: EncodingLevel):
    bits_per_channel = _BITS_PER_CHANNEL[level]
    channels_per_byte = 8 // bits_per_channel
    mask = np.uint8((1 << bits_per_channel) - 1)
    return bits_per_channel, channels_per_byte, mask


def _pack_header(secret_len: int, secret_type: int, shape=None) -> bytes:
    header = struct.pack(">IB", secret_len, secret_type)
    if secret_type == _TYPE_IMAGE and shape is not None:
        width, height, channels = shape
        header += struct.pack(">HHH", width, height, channels)
    return header


def _rgba_idx(rgb_idx: int) -> int:
    # L'array piatto è RGBA (4 canali a pixel), ma i bit del segreto vivono solo
    # nei canali RGB. L'indice `rgb_idx` conta i canali RGB; lo mappa nell'indice
    # dell'array RGBA saltando il canale alpha (ogni 4° posizione).
    return rgb_idx + (rgb_idx // 3)


def _write_byte(image_flat, rgb_idx, byte, bits_per_channel, mask):
    channels_per_byte = 8 // bits_per_channel
    for pos in range(channels_per_byte):
        chunk = (byte >> (pos * bits_per_channel)) & mask
        i = _rgba_idx(rgb_idx)
        image_flat[i] = (image_flat[i] & ~mask) | chunk
        rgb_idx += 1
    return rgb_idx


def _read_byte(image_flat, rgb_idx, bits_per_channel, mask):
    channels_per_byte = 8 // bits_per_channel
    byte = 0
    for pos in range(channels_per_byte):
        i = _rgba_idx(rgb_idx)
        chunk = int(image_flat[i]) & mask
        byte |= chunk << (pos * bits_per_channel)
        rgb_idx += 1
    return byte, rgb_idx


def _unpack_header(payload, level: EncodingLevel):
    bits_per_channel, channels_per_byte, mask = _params(level)
    rgb_idx = 0
    secret_len = 0
    for i in range(_HEADER_LEN_BYTES):
        # Big-endian: il byte 0 è il più significativo
        byte, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        secret_len |= int(byte) << (8 * (_HEADER_LEN_BYTES - 1 - i))
    type_byte, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
    secret_type = int(type_byte)
    shape = None
    if secret_type == _TYPE_IMAGE:
        w_hi, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        w_lo, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        w = (int(w_hi) << 8) | int(w_lo)
        h_hi, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        h_lo, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        h = (int(h_hi) << 8) | int(h_lo)
        c_hi, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        c_lo, rgb_idx = _read_byte(payload, rgb_idx, bits_per_channel, mask)
        c = (int(c_hi) << 8) | int(c_lo)
        shape = (w, h, c)
    return secret_len, secret_type, shape


def required_channels(size, level: EncodingLevel) -> int:
    _, channels_per_byte, _ = _params(level)
    return size * channels_per_byte


def encode(image: Image.Image, secret, level: EncodingLevel):
    try:
        secret_array = utils.to_array(secret)
    except TypeError as e:
        raise ValueError(str(e))

    if isinstance(secret, Image.Image):
        secret_type = _TYPE_IMAGE
        width, height = secret.size
        shape = (width, height, 3)
    else:
        secret_type = _TYPE_TEXT
        shape = None

    bits_per_channel, _, mask = _params(level)
    header = _pack_header(len(secret_array), secret_type, shape)
    payload = np.frombuffer(header + secret_array.tobytes(), dtype=np.uint8)

    image_flat = utils.image_to_flat_rgba(image)
    # I bit del segreto occupano solo i canali RGB: servono size * channels_per_byte
    # "slot" RGB, che nell'array RGBA corrispondono a piu' posizioni (c'e' l'alpha).
    if required_channels(len(payload), level) > image_flat.size - (
        image_flat.size // 4
    ):
        raise ValueError(
            "L'immagine di copertura è troppo piccola per nascondere il segreto "
            f"(necessari {required_channels(len(payload), level)} canali RGB, "
            f"disponibili {image_flat.size - image_flat.size // 4})"
        )

    rgb_idx = 0
    for byte in payload:
        rgb_idx = _write_byte(image_flat, rgb_idx, int(byte), bits_per_channel, mask)

    return image_flat


def decode(image: Image.Image, level: EncodingLevel):
    bits_per_channel, channels_per_byte, mask = _params(level)
    image_flat = utils.image_to_flat_rgba(image)

    # Legge prima l'header (lunghezza + tipo) per sapere quanto spazio occupa
    header_len_rgb = (_HEADER_LEN_BYTES + _HEADER_TYPE_BYTES) * channels_per_byte
    if header_len_rgb > image_flat.size - (image_flat.size // 4):
        raise ValueError("L'immagine non contiene un segreto valido")

    secret_len, secret_type, shape = _unpack_header(image_flat, level)

    if secret_type not in (_TYPE_TEXT, _TYPE_IMAGE):
        raise ValueError("L'immagine non contiene un segreto valido")

    # Offset dati: header completo (inclusi gli eventuali 6 byte di shape per immagini)
    header_total_bytes = _HEADER_LEN_BYTES + _HEADER_TYPE_BYTES
    if secret_type == _TYPE_IMAGE:
        header_total_bytes += _HEADER_SHAPE_BYTES
    rgb_idx = header_total_bytes * channels_per_byte

    if rgb_idx + secret_len * channels_per_byte > image_flat.size - (
        image_flat.size // 4
    ):
        raise ValueError("L'immagine non contiene un segreto valido")

    data = bytearray()
    for _ in range(secret_len):
        byte, rgb_idx = _read_byte(image_flat, rgb_idx, bits_per_channel, mask)
        data.append(byte)

    if secret_type == _TYPE_TEXT:
        return "text", data.decode("utf-8")
    else:
        width, height, channels = shape
        arr = np.frombuffer(bytes(data), dtype=np.uint8).reshape(
            height, width, channels
        )
        return "image", Image.fromarray(arr, "RGB")
