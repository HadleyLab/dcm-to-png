import os
import io

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
    fileName = request.query.get("fileName")
    root_path = "/ipfs-nodejs/dicom-files"
    image = convert_dcm_to_png(f"{root_path}/{fileName}")
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        contents = output.getvalue()
    resp = web.StreamResponse(status=200)
    resp.headers["Content-Type"] = "image/png"
    await resp.prepare(request)
    await resp.write(contents)
    return resp


app = web.Application()
app.add_routes([web.get("/", handle), web.get("/{fileName}", handle)])

if __name__ == "__main__":
    web.run_app(app, port=8080)
