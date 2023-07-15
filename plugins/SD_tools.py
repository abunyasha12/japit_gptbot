from typing import Literal
import base64

from datetime import datetime
import io
from pathlib import Path

import discord
import httpx

from PIL import Image, PngImagePlugin

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

sdconfig = Path("sdconfig.csv")

LORALIST: list[discord.app_commands.Choice] = []
RAW_LORALIST: str = ""

with open("sdconfig.csv") as lora_file:
    RAW_LORALIST = lora_file.read()
    LORALIST.extend(discord.app_commands.Choice(name=line, value=line) for line in RAW_LORALIST.split("\n"))


resolutions = Literal["448", "512", "640", "704", "768", "832", "896"]

upscalers = Literal["R-ESRGAN 4x+ Anime6B", "4x_foolhardy_Remacri"]

base_negative = "blurry, EasyNegative, badhandv4"

client = httpx.AsyncClient()


class file_ops:
    async def add_lora(self, lora_filename: str) -> str:
        with sdconfig.open("a+") as f:
            f.write(f'<lora:{lora_filename.replace(".safetensors", "").replace(".pt", "").strip()}:1>\n')
            # f.write(f'<lora:{".".join(lora_filename.split(".")[-1:-99])}:1>\n')
            f.seek(0)
            return f.read()

    async def del_lora(self, lora_filename: str) -> str:
        with sdconfig.open("r") as fin:
            # interm = [line for line in fin.readlines() if not line.startswith(lora_filename)]
            interm = [line for line in fin.readlines() if lora_filename not in line]

        with sdconfig.open("w+") as fout:
            for line in interm:
                fout.write(line)

            fout.seek(0)
            return fout.read()

    async def get_lora(self) -> str:
        with sdconfig.open("r") as f:
            return f.read()


def clean_prompt(prompt: str, sfw: bool = True) -> str:
    return ", ".join(w for _w in prompt.split(",") if (w := _w.strip().lower()) and w not in filter_words)


def refresh_loras() -> None:
    """Refreshes list of LoRas"""

    LORALIST.clear()
    with open("sdconfig.csv") as lora_file:
        RAW_LORALIST = lora_file.read()
        LORALIST.extend(discord.app_commands.Choice(name=line, value=line) for line in RAW_LORALIST.split("\n"))


def dt_os() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


async def logimage(url_list: list[str]) -> list[str]:
    ret_list: list[str] = []
    for ind, link in enumerate(url_list):
        resp = await client.get(link)
        fname = f"images/{dt_os()}_{ind}_image.png"
        with open(fname, "wb") as f:
            f.write(resp.content)
        ret_list.append(fname)
    return ret_list


class ImgNotFound(Exception):
    pass


class ImgTooLarge(Exception):
    pass


class SDTimeout(Exception):
    pass


async def checksd() -> bool:
    try:
        resp = await client.get(url=f"{SD_API_URL}/", timeout=3)
        return resp.status_code == 200
    except Exception as e:
        print(e.__class__.__name__)
        return False


async def image_from_bytes_to_b64str(image: bytes) -> str:
    return base64.b64encode(image).decode()


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
        "steps": 19,
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


async def img2img(prompt: str, vert: int, hor: int, denoising: float, image_b64_string: str, negative: str, sfw: bool = True) -> list[str]:
    if negative == "":
        negative = base_negative
    if sfw:
        neg = negative + ", nude, pussy, nipples"
    else:
        neg = negative
    genname = f"{dt_os()}_image"
    filenames = []
    # try:
    #     im2im_i = await image_from_url_to_b64str(im2im_url)
    # except Exception:
    #     raise
    if vert > 640 or hor > 640:
        batch = 1
    else:
        batch = 2
    gen_param = {
        "init_images": [image_b64_string],
        "resize_mode": 1,
        "denoising_strength": denoising,
        "prompt": prompt,
        "sampler_name": "DPM++ 2S a Karras",
        "batch_size": batch,
        "n_iter": 1,
        "steps": 19,
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


async def upscale(image_b64_string: str, scale_factor: float, upscaler: str):
    genname = f"{dt_os()}_image"
    # im_b64 = await image_from_url_to_b64str(image_url)

    scale_factor = max(min(scale_factor, 4), 1)
    gen_param = {
        "resize_mode": 0,
        "upscaling_resize": scale_factor,
        "upscaler_1": upscaler,
        "image": image_b64_string,
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
