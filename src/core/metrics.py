import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim_skimage


def ssim(img_a: Image.Image, img_b: Image.Image) -> float:

    if img_a.size != img_b.size:
        raise ValueError(
            f"Impossibile calcolare SSIM: dimensioni diverse {img_a.size} vs {img_b.size}"
        )

    arr_a = np.array(img_a.convert("RGB"))
    arr_b = np.array(img_b.convert("RGB"))

    # channel_axis=-1 indica che l'ultimo asse contiene i canali RGB (H, W, 3)
    score = ssim_skimage(arr_a, arr_b, channel_axis=-1, data_range=255)
    return float(score)
