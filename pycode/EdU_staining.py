import os
from PIL import Image
from PIL.ExifTags import TAGS
from skimage import io
import skimage.filters as skf_filters
import numpy as np
import pandas as pd
import czifile

img_dir = "C:/jklai/project/rice_heat-stress/experiments/EdU/WT-vs-mutants_Mock_20260128/CZI"
img_list = [i for i in os.listdir(img_dir) if i.endswith((".czi"))]

output_folder = os.path.join(os.path.dirname(img_dir), "OUT_" + os.path.basename(img_dir))
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

data = {
    "img_name": [], 
    "ntrack": [],
    "Zstacks": [],
    "img_size_pixels": [],
    "img_size_um": [],
    "resolution (um/pixel)": [],
    "area": [], 
    "total_intensity": [], 
    "avg_intensity": [],
    "distance_from_root_tip_pixels": [],
    "note": []
}

for i in img_list:
    czi = czifile.CziFile(os.path.join(img_dir, i))
    Metadata = czi.metadata(raw=False)["ImageDocument"]["Metadata"]
    ImageScaling = Metadata["ImageScaling"]
    ImagePixelSize, _ = ImageScaling["ImagePixelSize"]
    Magnification = ImageScaling["ScalingComponent"][1]["Magnification"]  # MTBObjectiveChanger
    microns_per_pixel = ImagePixelSize / Magnification
    pixels_per_micron = Magnification / ImagePixelSize

    czi_arr = czi.asarray()
    _, _, track, zstack, width, height, _ = czi_arr.shape
    
    img = czi_arr[0, 0, 0, :, :, :, 0]
    img = np.max(img, axis=0)
    
    if img.dtype != "uint8":
        img = (img - img.min()) / (img.max() - img.min()) * 255.0
        img = img.astype(np.uint8)
    
    img[img < 10] = 0

    total_intensity = img.sum()
    staining_area = np.sum(img > 0)
    avg_intensity = total_intensity / staining_area

    data["img_name"].append(i)
    data["ntrack"].append(track)
    data["Zstacks"].append(zstack)
    data["img_size_pixels"].append(f'{height} x {width}')
    data["img_size_um"].append(f'{height * microns_per_pixel} x {width * microns_per_pixel}')
    data["resolution (um/pixel)"].append(microns_per_pixel)
    data["area"].append(staining_area)
    data["total_intensity"].append(total_intensity)
    data["avg_intensity"].append(avg_intensity)
    data["distance_from_root_tip_pixels"].append("")
    data["note"].append("")

    RGB_img = np.zeros((width, height, 3), dtype = np.uint8)
    RGB_img[:, :, 1] = img  # insert to green channel
    RGB_img = Image.fromarray(RGB_img, mode="RGB")
    RGB_img.save(os.path.join(output_folder, f"{i.removesuffix('.czi')}.tiff"), "TIFF")

df0 = pd.DataFrame.from_dict(data)
df0.to_csv(os.path.join(output_folder, f"OUT_EdU.csv"), index=False)

