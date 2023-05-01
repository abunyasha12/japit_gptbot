import httpx
from datetime import datetime
from PIL import Image, PngImagePlugin
import base64
import io


SD_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

SD_API_URL = 'http://192.168.0.105:7860'

filterwords = ["nude", "nsfw", "naked", "pussy", "nipples",
               "bare skin", "pussy juice", "fucking", "stripped", "bare-skinned", "pussy juice", "NSFW", "NUDE", "NAKED", "PUSSY", "NIPPLES"]

client = httpx.AsyncClient(timeout=3)


def dt_os():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class ImgNotFound(Exception):
    pass


class ImgTooLarge(Exception):
    pass


async def checksd() -> int:
    try:
        resp = await client.get(url=f'{SD_API_URL}/')
    except Exception as e:
        print(e.__class__.__name__)
        return 0
    return resp.status_code


async def image_from_url_to_b64str(image_url) -> str:
    try:
        resp = await client.get(image_url)
        if resp.status_code != 200:
            raise ImgNotFound
        if len(resp.content) > 1000000:
            raise ImgTooLarge
        im2im = base64.b64encode(resp.content).decode()
        return im2im
    except httpx.ConnectTimeout:
        raise ImgNotFound
    except httpx.ConnectError:
        raise ImgNotFound
    except Exception as e:
        print(e.__class__.__name__)
        raise


async def txt2img(prompt: str,
                  height: int,
                  width: int,
                  negative: str = "blurry, EasyNegative",
                  sfw: bool = True):
    pl = prompt.split(sep=", ")
    if sfw:
        neg = negative + ", nude, pussy, nipples"
        filtered = ", ".join([i for i in pl if i not in filterwords])
    else:
        neg = negative
        filtered = ", ".join(pl)
    genname = f"{dt_os()}_image"
    filenames = []
    if height > 640 or width > 640:
        batch = 1
    else:
        batch = 2
    generation_parameters = {
        "prompt": filtered,
        "sampler_name": "DPM++ 2S a Karras",
        "batch_size": batch,
        "n_iter": 1,
        "steps": 21,
        "width": width,
        "height": height,
        "negative_prompt": neg
    }
    response = await client.post(
        url=f'{SD_API_URL}/sdapi/v1/txt2img', json=generation_parameters)
    r = response.json()
    for ind, img in enumerate(r['images']):
        image = Image.open(io.BytesIO(base64.b64decode(img)))
        png_payload = {
            "image": "data:image/png;base64," + img
        }
        response2 = await client.post(
            url=f'{SD_API_URL}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f'images_sd/{genname}_{ind}.png')
        filenames.append(f'images_sd/{genname}_{ind}.png')
    return filenames


async def img2img(prompt: str,
                  vert: int,
                  hor: int,
                  denoising: float,
                  im2im_url: str,
                  negative: str = "blurry, EasyNegative, nude, nsfw, naked, pussy, nipples",
                  sfw: bool = True
                  ):
    if sfw:
        for fw in filterwords:
            prompt = prompt.replace(fw, "")
    genname = f"{dt_os()}_image"
    filenames = []
    try:
        im2im_i = await image_from_url_to_b64str(im2im_url)
    except Exception:
        raise
    if vert > 640 or hor > 640:
        batch = 1
    else:
        batch = 2
    generation_parameters = {
        "init_images": [im2im_i],
        "resize_mode": 1,
        "denoising_strength": denoising,
        "prompt": prompt,
        "sampler_name": "DPM++ 2S a Karras",
        "batch_size": batch,
        "n_iter": 1,
        "steps": 21,
        "width": hor,
        "height": vert,
        "negative_prompt": negative
    }
    response = await client.post(
        url=f'{SD_API_URL}/sdapi/v1/img2img', json=generation_parameters)
    for ind, img in enumerate(response.json()['images']):
        try:
            image = Image.open(io.BytesIO(base64.b64decode(img)))
        except:
            raise
        png_payload = {
            "image": "data:image/png;base64," + img
        }
        response2 = await client.post(
            url=f'{SD_API_URL}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f'images_sd/{genname}_{ind}.png')
        filenames.append(f'images_sd/{genname}_{ind}.png')
    return filenames
