from __future__ import annotations

import discord
from discord import app_commands
from discord.app_commands import TranslationContextLocation as CL


class MyTranslator(app_commands.Translator):
    async def translate(self,
                        string: app_commands.locale_str,
                        locale: discord.Locale,
                        context: app_commands.TranslationContext) -> str | None:
        text = str(string)
        loc = context.location
        if (
            loc == CL.choice_name
            or loc == CL.parameter_name
            or loc == CL.command_name
        ):
            return text
        if locale == discord.Locale.russian:
            match text:
                case "Request image from Stable Diffusion (may not be available)":
                    return "Запросить изображение через Stable Diffusion (может быть недоступно) TEST1"
                case "Request chat completion from OpenAI ChatGPT":
                    return "Запросить ответ от CHatGPT"
                case "Request image from DALL-E":
                    return "Запросить изображение от DALL-E"
                case "Image prompt":
                    return "Промпт для изображения"
                case "Negative prompt":
                    return "Негативный промпт"
                case "Resolution, X*X pixels":
                    return "Разрешение, X*X пикселей"
                case "Vertical resolution, pixels":
                    return "Вертикальное разрешение, пикселей"
                case "Horizontal resolution, pixels":
                    return "Горизонтальное разрешение, пикселей"
                case "First LoRa":
                    return "Первая LoRa"
                case "Second LoRa":
                    return "Вторая LoRa"
                case "URL for img2img image":
                    return "Ссылка на изображение для img2img"
                case "Denoising value 0 - 1 with 0.05 increments":
                    return "Значение denoising от 0 до 1 с шагом 0.05"
                case "Your message to ChatGPT":
                    return "Запрос для ChatGPT"
                case "Try again in {round(error.retry_after)} seconds.":
                    return "Попробуйте еще раз через {round(error.retry_after)} сек"
                case _e:
                    print(
                        f"COULD NOT TRANSLATE TO RUSSIAN: '{text}' LOCATION: '{loc}'")
                    return text
        else:
            return text
