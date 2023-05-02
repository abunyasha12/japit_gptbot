import httpx
from datetime import datetime
from PIL import Image, PngImagePlugin
import base64
import io
from typing import Literal

SD_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

SD_API_URL = 'http://192.168.0.103:7860'

filterwords = ["nude", "nsfw", "naked", "pussy", "nipples",
               "bare skin", "pussy juice", "fucking", "stripped",
               "bare-skinned", "pussy juice"]

loralist = Literal[' <lora:anime_screencap_v2-000030:1>',
                   ' <lora:animeoutlineV4_16:1>',
                   ' <lora:helltaker:0.7>',
                   ' <lora:hutao:0.7>',
                   ' <lora:thickline_fp16:1>']

resolutions = Literal["448", "512", "640", "704", "768"]

client = httpx.AsyncClient()


def cleanprompt(prompt: str, sfw: bool = True) -> str:
    pl = []
    for i in prompt.lower().split(sep=','):
        if i != '':
            pl.append(i.replace('.', '').strip())
    print(len(pl))
    if sfw:
        for word in filterwords:
            for pl_wrd in list(pl):
                if word in pl_wrd:
                    pl.remove(pl_wrd)
        filtered = ", ".join(pl)
    else:
        filtered = ", ".join(pl)
    return filtered


def dt_os() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class ImgNotFound(Exception):
    pass


class ImgTooLarge(Exception):
    pass


class SDTimeout(Exception):
    pass


async def checksd() -> bool:
    try:
        resp = await client.get(url=f'{SD_API_URL}/', timeout=3)
        if resp.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(e.__class__.__name__)
        return False


async def image_from_url_to_b64str(image_url) -> str:
    try:
        resp = await client.get(image_url, timeout=30)
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
                  negative: str,
                  sfw: bool = True):
    if negative == '':
        negative = "blurry, EasyNegative, badhandv4"
    if sfw:
        neg = negative + ", nude, pussy, nipples"
    else:
        neg = negative
    genname = f"{dt_os()}_image"
    filenames = []
    if height > 640 or width > 640:
        batch = 1
    else:
        batch = 2
    generation_parameters = {
        "prompt": prompt,
        "sampler_name": "DPM++ 2S a Karras",
        "batch_size": batch,
        "n_iter": 1,
        "steps": 21,
        "width": width,
        "height": height,
        "negative_prompt": neg
    }
    print(f'prompt: {prompt} \nnegative prompt: {neg}')
    try:
        response = await client.post(url=f'{SD_API_URL}/sdapi/v1/txt2img', json=generation_parameters, timeout=30)
    except httpx.ConnectTimeout:
        raise SDTimeout
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
    try:
        response = await client.post(url=f'{SD_API_URL}/sdapi/v1/img2img', json=generation_parameters, timeout=30)
    except httpx.ConnectTimeout:
        raise SDTimeout
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
