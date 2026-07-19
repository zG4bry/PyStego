import numpy as np
from PIL import Image

from src.core.encoder import encode, decode, EncodingLevel
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


def test_alpha_preserved():
    # Una cover con alpha parziale deve conservare l'alpha dopo encode+save+decode
    cover = Image.new("RGBA", (64, 64), (10, 20, 30, 123))
    flat = encode(cover, "segreto", EncodingLevel.LOW)
    arr = flat.reshape(64, 64, 4)
    assert np.all(arr[:, :, 3] == 123)  # alpha intatto

    path = "/tmp/pystego_alpha.png"
    utils.save(flat, 64, 64, path, "png")
    loaded = utils.load(path)
    assert np.all(np.array(loaded)[:, :, 3] == 123)  # alpha preservato su disco


def test_roundtrip_text_png_on_disk():
    secret = "testo su disco"
    flat = encode(_cover_rgba(), secret, EncodingLevel.HIGH)
    path = "/tmp/pystego_test_out.png"
    utils.save(flat, 128, 128, path, "png")
    loaded = utils.load(path)
    kind, out = decode(loaded, EncodingLevel.HIGH)
    assert kind == "text"
    assert out == secret


def test_roundtrip_image_png_on_disk():
    secret = Image.new("RGB", (16, 16), (1, 2, 3))
    flat = encode(_cover_rgba(), secret, EncodingLevel.MED)
    path = "/tmp/pystego_test_img.png"
    utils.save(flat, 128, 128, path, "png")
    loaded = utils.load(path)
    kind, out = decode(loaded, EncodingLevel.MED)
    assert kind == "image"
    assert np.array_equal(np.array(out), np.array(secret))


def test_too_small_cover_raises():
    tiny = Image.new("RGB", (2, 2), (0, 0, 0))
    secret = "x" * 1000
    import pytest
    with pytest.raises(ValueError):
        encode(tiny, secret, EncodingLevel.LOW)


def test_decode_wrong_level_raises_or_differs():
    secret = "segreto di prova"
    flat = encode(_cover_rgba(), secret, EncodingLevel.LOW)
    # Decodifica con livello diverso: i bit non combaciano -> lunghezza/header invalido
    import pytest
    with pytest.raises(ValueError):
        decode(Image.fromarray(flat.reshape(128, 128, 4), "RGBA"), EncodingLevel.HIGH)
