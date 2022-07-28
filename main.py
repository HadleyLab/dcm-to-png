import os

import numpy as np
import pydicom
from aiohttp import web
from PIL import Image as Img


def get_names(path):
    names = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext in [".dcm"]:
                names.append(filename)
    return names


def convert_dcm_to_png(path_with_filename):
    im = pydicom.dcmread(path_with_filename)
    im = im.pixel_array.astype(float)
    rescaled_image = (np.maximum(im, 0) / im.max()) * 255
    final_image = np.uint8(rescaled_image)
    final_image = Img.fromarray(final_image)
    return final_image


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


async def handle(request):
    root_path = "../ipfs-node-js/"
    dicom_folder = "dicom-files"
    png_folder = "png-files"
    names = get_names(root_path + dicom_folder)
    create_folder(root_path + png_folder)
    for name in names:
        image = convert_dcm_to_png(root_path + dicom_folder + "/" + name)
        image.save(root_path + png_folder + "/" + name + ".png")
    return web.Response(text="ok")


app = web.Application()
app.add_routes([web.get("/", handle), web.get("/{name}", handle)])

if __name__ == "__main__":
    web.run_app(app, port=8089)
