import pytest
from PIL import Image
from src.core import metrics
from src.core.encoder import encode, EncodingLevel
from src.utils import utils


def _cover():
    return Image.new("RGB", (128, 128), (12, 34, 56))


def test_ssim_identical():
    img = _cover()
    assert metrics.ssim(img, img) == pytest.approx(1.0)


def test_ssim_different_size_raises():
    img_a = Image.new("RGB", (128, 128))
    img_b = Image.new("RGB", (64, 64))
    with pytest.raises(ValueError):
        metrics.ssim(img_a, img_b)


def test_ssim_stego_high_quality():
    cover = _cover()
    secret = "a" * 1000

    flat = encode(cover, secret, EncodingLevel.LOW)
    stego = utils.flat_to_image(flat, cover.width, cover.height)

    score = metrics.ssim(cover, stego)
    assert 0.99 < score < 1.0
