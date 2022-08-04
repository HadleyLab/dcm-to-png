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
    rescaled_image = (np.maximum(im, 0) / im.max()) * 255  # float pixels
    final_image = np.uint8(rescaled_image)  # integers pixels
    final_image = Img.fromarray(final_image)
    return final_image


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


async def handle(request):
    patientId = request.match_info.get("patientId", "empty")
    root_path = "../ipfs-nodejs/"
    dicom_folder = "dicom-files"
    png_folder = "png-files"
    names = get_names(f"{root_path}{dicom_folder}")
    create_folder(f"{root_path}{png_folder}")
    create_folder(f"{root_path}/{png_folder}/{patientId}")
    for name in names:
        image = convert_dcm_to_png(f"{root_path}{dicom_folder}/{name}")
        image.save(f"{root_path}{png_folder}/{patientId}/{name}.png")
        print(f"{root_path}{png_folder}/{patientId}/{name}.png saved")
    for name in names:
        print("start remove")
        os.remove(f"{root_path}{dicom_folder}/{name}")
        print(f"{root_path}{dicom_folder}/{name} removed")
    print("ok")
    return web.Response(text="ok")


app = web.Application()
app.add_routes([web.get("/", handle), web.get("/{patientId}", handle)])

if __name__ == "__main__":
    web.run_app(app, port=8080)
