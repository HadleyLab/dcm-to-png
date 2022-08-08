from io import BytesIO

import aiohttp
import async_timeout
import numpy as np
import pydicom
from aiohttp import web
from PIL import Image as Img


async def download(download_url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(120):
            async with session.get(download_url) as response:
                dcm = await response.content.read()
                image = convert_dcm_to_png(dcm)
    return image


def convert_dcm_to_png(file):
    im = pydicom.dcmread(BytesIO(file))
    im = im.pixel_array.astype(float)
    rescaled_image = (np.maximum(im, 0) / im.max()) * 255  # float pixels
    final_image = np.uint8(rescaled_image)  # integers pixels
    final_image = Img.fromarray(final_image)
    return final_image


async def handle(request):
    download_url = request.query["downloadUrl"]
    image = await download(download_url)
    with BytesIO() as output:
        image.save(output, format="PNG")
        contents = output.getvalue()
    resp = web.StreamResponse(status=200)
    resp.headers["Content-Type"] = "image/png"
    await resp.prepare(request)
    await resp.write(contents)
    return resp


app = web.Application()
app.add_routes([web.get("/get-png-image", handle)])

if __name__ == "__main__":
    web.run_app(app, port=8080)
