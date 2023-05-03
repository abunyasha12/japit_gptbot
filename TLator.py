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
            # or loc == CL.parameter_name
            # or loc == CL.command_name
        ):
            return text
        if locale == discord.Locale.russian:
            match text:
                # Команды
                case "chat":
                    return "чат"
                case "image":
                    return text
                case "sdimage":
                    return text
                case "img2img":
                    return text
                case "synchronise":
                    return text
                case "text":
                    return "текст"
                # Описания команд
                case "Request image from Stable Diffusion (may not be available)":
                    return "Запросить изображение через Stable Diffusion (может быть недоступно)"
                case "Request chat completion from OpenAI ChatGPT":
                    return "Запросить ответ от ChatGPT"
                case "Request image from DALL-E":
                    return "Запросить изображение от DALL-E"
                case "sync commands":
                    return "синхронизировать команды"
                # Описания параметров команд
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
                # Параметры команд
                case "prompt":
                    return "промпт"
                case "resolution":
                    return "разрешение"
                case "height":
                    return "высота"
                case "width":
                    return "ширина"
                case "negative":
                    return "негатив"
                case "denoising":
                    return text
                case "image_url":
                    return "ссылка_на_картинку"
                case "lora1":
                    return text
                case "lora2":
                    return text
                # Прочее
                case _e:
                    print(
                        f"COULD NOT TRANSLATE TO RUSSIAN: '{text}' LOCATION: '{loc}'")
                    return text
        # elif locale == discord.Locale.british_english or locale == discord.Locale.american_english:
        #     return text
        else:
            return text
