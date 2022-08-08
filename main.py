import io
import logging
import os

import aiohttp
import async_timeout
import numpy as np
import pydicom
from aiohttp import web
from PIL import Image as Img

dicom_files_path = "./dicom-files"


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


def clean_up(patient_id):
    path = f"{dicom_files_path}/{patient_id}"
    if os.path.exists(path):
        os.system(f"rm -rf {path}")
        logging.info(f"Removed {path}")
    else:
        logging.info(f"Folder {path} does not exist")


async def download(patient_id, file_name, download_url):
    create_folder(f"{dicom_files_path}/{patient_id}")
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(120):
            async with session.get(download_url) as response:
                with open(f"{dicom_files_path}/{patient_id}/{file_name}", "wb") as fd:
                    async for data in response.content.iter_chunked(1024):
                        fd.write(data)
    return "Successfully downloaded " + file_name


async def handle_convert_dcm(request):
    file_name = request.query.get("fileName")
    patient_id = request.query["patientId"]
    image = convert_dcm_to_png(f"{dicom_files_path}/{patient_id}/{file_name}")
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        contents = output.getvalue()
    resp = web.StreamResponse(status=200)
    resp.headers["Content-Type"] = "image/png"
    await resp.prepare(request)
    await resp.write(contents)
    return resp


async def handle_download_dcm(request):
    file_name = request.query["fileName"]
    patient_id = request.query["patientId"]
    download_url = str(request.url).split("downloadUrl=")[1]
    await download(patient_id, file_name, download_url)
    return web.Response(text="ok")


async def handle_clean_up(request):
    patient_id = request.query["patientId"]
    clean_up(patient_id)
    return web.Response(text="ok")


app = web.Application()
app.add_routes([web.get("/download-dcm", handle_download_dcm)])
app.add_routes([web.get("/clean-up", handle_clean_up)])
app.add_routes([web.get("/get-png-image", handle_convert_dcm)])

if __name__ == "__main__":
    web.run_app(app, port=8080)
