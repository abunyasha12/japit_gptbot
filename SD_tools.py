import httpx
from datetime import datetime
from PIL import Image, PngImagePlugin
import base64
import io
from typing import Literal
import discord

SD_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

SD_API_URL = "http://192.168.0.103:7860"

filter_words = [
    "nude",
    "nsfw",
    "naked",
    "pussy",
    "nipples",
    "bare skin",
    "fucking",
    "stripped",
    "bare-skinned",
    "topless",
]

LORALIST: list[discord.app_commands.Choice] = []

with open("sdconfig.csv") as lora_file:
    LORALIST.extend(discord.app_commands.Choice(name=line.rstrip("\n"), value=line.rstrip("\n")) for line in lora_file.readlines())


resolutions = Literal["448", "512", "640", "704", "768", "832", "896"]

upscalers = Literal["R-ESRGAN 4x+ Anime6B", "4x_foolhardy_Remacri"]

base_negative = "blurry, EasyNegative, badhandv4"

client = httpx.AsyncClient()


def clean_prompt(prompt: str, sfw: bool = True) -> str:
    return ", ".join(w for _w in prompt.split(",") if (w := _w.strip().lower()) and w not in filter_words)


def refresh_loras() -> None:
    """Refreshes list of LoRas"""
    LORALIST.clear()
    with open("sdconfig.csv") as lora_file:
        LORALIST.extend(discord.app_commands.Choice(name=line.rstrip("\n"), value=line.rstrip("\n")) for line in lora_file.readlines())


def dt_os() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


async def logimage(url) -> None:
    resp = await client.get(url)
    with open(f"images/{dt_os()}_image.png", "wb") as f:
        f.write(resp.content)


class ImgNotFound(Exception):
    pass


class ImgTooLarge(Exception):
    pass


class SDTimeout(Exception):
    pass


async def checksd() -> bool:
    try:
        resp = await client.get(url=f"{SD_API_URL}/", timeout=3)
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
        raise ImgTooLarge
    except httpx.ConnectError:
        raise ImgNotFound
    except Exception as e:
        print(e.__class__.__name__)
        raise


async def txt2img(prompt: str, height: int, width: int, negative: str, sfw: bool = True) -> list[str]:
    if negative == "":
        negative = base_negative
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
    gen_param = {
        "prompt": prompt,
        "sampler_name": "DPM++ 2S a Karras",
        "batch_size": batch,
        "n_iter": 1,
        "steps": 21,
        "width": width,
        "height": height,
        "negative_prompt": neg,
    }
    print(f"prompt: {prompt} \nnegative prompt: {neg}")
    try:
        response = await client.post(url=f"{SD_API_URL}/sdapi/v1/txt2img", json=gen_param, timeout=30)
    except httpx.ConnectTimeout:
        raise SDTimeout
    r = response.json()
    for ind, img in enumerate(r["images"]):
        image = Image.open(io.BytesIO(base64.b64decode(img)))
        png_payload = {"image": "data:image/png;base64," + img}
        response2 = await client.post(url=f"{SD_API_URL}/sdapi/v1/png-info", json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f"images_sd/{genname}_{ind}.png")
        filenames.append(f"images_sd/{genname}_{ind}.png")
    return filenames


async def img2img(
    prompt: str,
    vert: int,
    hor: int,
    denoising: float,
    im2im_url: str,
    negative: str,
    sfw: bool = True,
) -> list[str]:
    if negative == "":
        negative = base_negative
    if sfw:
        neg = negative + ", nude, pussy, nipples"
    else:
        neg = negative
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
    gen_param = {
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
        "negative_prompt": neg,
    }
    try:
        response = await client.post(url=f"{SD_API_URL}/sdapi/v1/img2img", json=gen_param, timeout=30)
    except httpx.ConnectTimeout:
        raise SDTimeout
    for ind, img in enumerate(response.json()["images"]):
        try:
            image = Image.open(io.BytesIO(base64.b64decode(img)))
        except:
            raise
        png_payload = {"image": "data:image/png;base64," + img}
        response2 = await client.post(url=f"{SD_API_URL}/sdapi/v1/png-info", json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f"images_sd/{genname}_{ind}.png")
        filenames.append(f"images_sd/{genname}_{ind}.png")
    return filenames


async def upscale(image_url: str, scale_factor: float, upscaler: str):
    genname = f"{dt_os()}_image"
    im_b64 = await image_from_url_to_b64str(image_url)

    scale_factor = max(min(scale_factor, 4), 1)
    print(scale_factor)
    gen_param = {
        "resize_mode": 0,
        "upscaling_resize": scale_factor,
        "upscaler_1": upscaler,
        "image": im_b64,
    }
    try:
        response = await client.post(url=f"{SD_API_URL}/sdapi/v1/extra-single-image", json=gen_param, timeout=30)
    except httpx.ConnectTimeout:
        raise SDTimeout
    except Exception:
        raise
    response = response.json()
    Image.open(io.BytesIO(base64.b64decode(response["image"]))).save(f"extras/{genname}.png")
    return f"extras/{genname}.png"
