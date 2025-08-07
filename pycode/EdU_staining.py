import os
from PIL import Image
from PIL.ExifTags import TAGS
from skimage import io
import skimage.filters as skf_filters
import numpy as np
import pandas as pd
import czifile

from z_projection import Z_projection


img_dir = "C:/jklai/project/rice_heat-stress/experiments/EdU/OsRGF1_gradient/osrgf1-7_0-1-10-100-1000pM_20250805"
img_list = [i for i in os.listdir(img_dir) if i.endswith((".czi"))]

#df0 = pd.DataFrame(columns = ["img_name", "area", "total_intensity"])
data = {
    "img_name": [], 
    "ntrack": [],
    "Zstacks": [],
    "img_size_pixels": [],
    "img_size_um": [],
    "resolution (um/pixel)": [],
    "area": [], 
    "total_intensity": [], 
    "avg_intensity": []
}

for i in img_list:
    #img = czifile.imread(os.path.join(img_dir, i))
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
    img = Z_projection(img, methods="max_intensity")
    img[img < 100] = 0

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
    
    #df0 = pd.concat([ 
    #    df0, 
    #    pd.DataFrame({
    #        "img_name": [i], 
    #        "img_size_pixels": [f'{height} x {width}'],
    #        "img_size_um": [f'{height * microns_per_pixel} x {width * microns_per_pixel}'],
    #        "resolution (um/pixel)": [microns_per_pixel],
    #        "area": [staining_area], 
    #        "total_intensity": [total_intensity], 
    #        "avg_intensity": [avg_intensity]
    #    })
    #])

    RGB_img = np.zeros((width, height, 3), dtype = np.uint8)
    RGB_img[:, :, 1] = img  # insert to green channel
    RGB_img = Image.fromarray(RGB_img, mode="RGB")
    RGB_img.save(os.path.join(img_dir, f"{i.removesuffix('.czi')}.tiff"), "TIFF")

df0 = pd.DataFrame.from_dict(data)
df0.to_csv(os.path.join(img_dir, "total_intensity.csv"), index=False)

