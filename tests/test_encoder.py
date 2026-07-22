import numpy as np
import pytest
from PIL import Image

from src.core.encoder import encode, decode, EncodingLevel, required_channels
from src.utils import utils


def _cover_rgba():
    return Image.new("RGBA", (128, 128), (12, 34, 56, 200))


def test_roundtrip_text_all_levels():
    secret = "messaggio segreto con accenti àòù €"
    for level in EncodingLevel:
        flat = encode(_cover_rgba(), secret, level)
        kind, out = decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), level)
        assert kind == "text"
        assert out == secret


def test_roundtrip_image_all_levels():
    secret = Image.new("RGB", (16, 16), (200, 100, 50))
    for level in EncodingLevel:
        flat = encode(_cover_rgba(), secret, level)
        kind, out = decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), level)
        assert kind == "image"
        assert np.array_equal(np.array(out), np.array(secret))


def test_roundtrip_image_rectangular_all_levels():
    secret = Image.new("RGB", (40, 10), (200, 100, 50))
    for level in EncodingLevel:
        flat = encode(_cover_rgba(), secret, level)
        kind, out = decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), level)
        assert kind == "image"
        assert np.array_equal(np.array(out), np.array(secret))


def test_encode_invalid_secret_type_raises_valueerror():
    with pytest.raises(ValueError):
        encode(_cover_rgba(), 12345, EncodingLevel.LOW)


def test_alpha_preserved(tmp_path):
    cover = Image.new("RGBA", (64, 64), (10, 20, 30, 123))
    flat = encode(cover, "segreto", EncodingLevel.LOW)
    arr = flat.reshape(64, 64, 4)
    assert np.all(arr[:, :, 3] == 123)

    path = tmp_path / "pystego_alpha.png"
    utils.save(flat, 64, 64, str(path), "png")
    loaded = utils.load(str(path))
    assert np.all(np.array(loaded)[:, :, 3] == 123)


def test_roundtrip_image_rgba_all_levels():
    secret = Image.new("RGBA", (16, 16), (200, 100, 50, 180))
    for level in EncodingLevel:
        flat = encode(_cover_rgba(), secret, level)
        kind, out = decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), level)
        assert kind == "image"
        assert out.mode == "RGBA"
        assert np.array_equal(np.array(out), np.array(secret))


def test_roundtrip_text_png_on_disk(tmp_path):
    secret = "testo su disco"
    flat = encode(_cover_rgba(), secret, EncodingLevel.HIGH)
    path = tmp_path / "pystego_test_out.png"
    utils.save(flat, 128, 128, str(path), "png")
    loaded = utils.load(str(path))
    kind, out = decode(loaded, EncodingLevel.HIGH)
    assert kind == "text"
    assert out == secret


def test_roundtrip_image_png_on_disk(tmp_path):
    secret = Image.new("RGB", (16, 16), (1, 2, 3))
    flat = encode(_cover_rgba(), secret, EncodingLevel.MED)
    path = tmp_path / "pystego_test_img.png"
    utils.save(flat, 128, 128, str(path), "png")
    loaded = utils.load(str(path))
    kind, out = decode(loaded, EncodingLevel.MED)
    assert kind == "image"
    assert np.array_equal(np.array(out), np.array(secret))


def test_too_small_cover_raises():
    tiny = Image.new("RGB", (2, 2), (0, 0, 0))
    secret = "x" * 1000
    with pytest.raises(ValueError):
        encode(tiny, secret, EncodingLevel.LOW)


def test_decode_wrong_level_raises():
    secret = "segreto di prova"
    flat = encode(_cover_rgba(), secret, EncodingLevel.LOW)
    with pytest.raises(ValueError):
        decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), EncodingLevel.HIGH)


def test_decode_tiny_image_raises():
    tiny = Image.new("RGBA", (1, 1), (0, 0, 0, 255))
    with pytest.raises(ValueError):
        decode(tiny, EncodingLevel.LOW)


def test_required_channels():
    assert required_channels(100, EncodingLevel.LOW) == 800
    assert required_channels(100, EncodingLevel.MED) == 400
    assert required_channels(100, EncodingLevel.HIGH) == 200


def test_roundtrip_empty_string():
    secret = ""
    for level in EncodingLevel:
        flat = encode(_cover_rgba(), secret, level)
        kind, out = decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), level)
        assert kind == "text"
        assert out == ""


def test_roundtrip_single_byte_string():
    secret = "X"
    for level in EncodingLevel:
        flat = encode(_cover_rgba(), secret, level)
        kind, out = decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), level)
        assert kind == "text"
        assert out == secret


def test_roundtrip_transparent_cover():
    cover = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    secret = "dato nascosto"
    flat = encode(cover, secret, EncodingLevel.MED)
    kind, out = decode(
        Image.fromarray(flat.reshape(64, 64, 4), "RGBA"), EncodingLevel.MED
    )
    assert kind == "text"
    assert out == secret
