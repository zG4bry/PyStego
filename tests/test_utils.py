import numpy as np
import pytest
from PIL import Image
from src.utils import utils


def test_text_to_array():
    result = utils.text_to_array("abc")
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.uint8
    assert list(result) == [97, 98, 99]


def test_text_to_array_unicode():
    result = utils.text_to_array("àòù")
    assert result.tobytes().decode("utf-8") == "àòù"


def test_text_to_array_invalid_type():
    with pytest.raises(TypeError, match="deve essere una stringa"):
        utils.text_to_array(123)


def test_img_to_array():
    img = Image.new("RGB", (2, 2), (10, 20, 30))
    result = utils.img_to_array(img)
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.uint8
    assert result.shape == (12,)


def test_img_to_array_invalid_type():
    with pytest.raises(TypeError, match="deve essere un'immagine"):
        utils.img_to_array("not_an_image")


def test_image_to_flat_rgba_rgb():
    img = Image.new("RGB", (2, 2), (10, 20, 30))
    result = utils.image_to_flat_rgba(img)
    assert result.shape == (16,)
    assert result.dtype == np.uint8


def test_image_to_flat_rgba_rgba():
    img = Image.new("RGBA", (2, 2), (10, 20, 30, 200))
    result = utils.image_to_flat_rgba(img)
    assert result.shape == (16,)
    assert result[3] == 200


def test_flat_to_image_roundtrip():
    original = Image.new("RGBA", (4, 4), (10, 20, 30, 200))
    flat = utils.image_to_flat_rgba(original)
    reconstructed = utils.flat_to_image(flat, 4, 4)
    assert np.array_equal(np.array(original), np.array(reconstructed))


def test_png_path_adds_extension():
    result = utils.png_path("/tmp/test")
    assert result == "/tmp/test.png"


def test_png_path_keeps_extension():
    result = utils.png_path("/tmp/test.png")
    assert result == "/tmp/test.png"


def test_save_and_load_roundtrip(tmp_path):
    img = Image.new("RGBA", (4, 4), (10, 20, 30, 200))
    flat = utils.image_to_flat_rgba(img)
    path = tmp_path / "out.png"
    utils.save(flat, 4, 4, str(path), "png")
    loaded = utils.load(str(path))
    assert np.array_equal(np.array(img), np.array(loaded))


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError, match="non trovata"):
        utils.load("/nonexistent/path.png")


def test_load_invalid_file(tmp_path):
    path = tmp_path / "invalid.txt"
    path.write_text("not an image")
    with pytest.raises(ValueError, match="Errore durante il caricamento"):
        utils.load(str(path))


def test_to_array_string():
    result = utils.to_array("abc")
    assert isinstance(result, np.ndarray)


def test_to_array_image():
    img = Image.new("RGB", (2, 2), (10, 20, 30))
    result = utils.to_array(img)
    assert isinstance(result, np.ndarray)


def test_to_array_invalid_type():
    with pytest.raises(TypeError, match="deve essere una stringa o un'immagine"):
        utils.to_array(12345)
