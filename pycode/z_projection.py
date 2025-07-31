import numpy as np

def Z_projection(img, dim="ZXY", methods = "max_intensity"):
    img = np.max(img, axis=0)
    if img.dtype != "uint8":
        img = img.astype(np.uint8)
    return img
