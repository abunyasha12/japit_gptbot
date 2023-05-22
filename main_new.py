import discord
from discord.ext import commands
from discord.ui import View, Button
from discord import app_commands
from discord.app_commands import locale_str as ls
import logging
import logging.handlers
import OA_tools as OA
import SD_tools as SD
from TLator import MyTranslator
from cdifflib import CSequenceMatcher
from itertools import islice
import re
from typing import Generator
from models.openai import ConversationLog
from starlette.config import Config
from starlette.datastructures import Secret


log = logging.getLogger()
logging.getLogger("openai").setLevel(logging.ERROR)
log.setLevel(logging.INFO)

fhandler = logging.handlers.TimedRotatingFileHandler("./logs/logfile.log", "D", backupCount=30, encoding="utf-8")
dt_fmt = "%Y-%m-%d %H:%M:%S"
fmt = logging.Formatter(
    "[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s:%(lineno)d] %(message)s",
    dt_fmt,
)
fhandler.setFormatter(fmt)
log.addHandler(fhandler)

chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
chandler.setFormatter(fmt)
log.addHandler(chandler)


config = Config(".env")

DISCORD_TOKEN = config("DISCORD_TOKEN", cast=Secret, default="")
OPENAI_TOKEN = config("OPENAI_TOKEN", cast=Secret, default="")
DEEPL_TOKEN = config("DEEPL_TOKEN", cast=Secret, default="")

guilds_ids = [
    208894633432973314,  # proving grounds
    340723151967092746,  # pizdec
    333700550862569472,  # japit
]

sfw_channels = [1093166962428882996, 831502411411095562]  # japit.gpt  # pg.general

users_allowed_to_sync = [142228355104636928, 264168634123812865]  # drug  # tiki

MAX_MSG_LEN = 1900


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guild_reactions = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)


class EnvelopeButton(Button):
    def __init__(self) -> None:
        super().__init__(emoji="✉️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.message is None:
            return
        await send_dm(interaction.message, interaction.user)


class CrossButton(Button):
    def __init__(self, sview) -> None:
        super().__init__(emoji="🗑️")
        self.sview = sview

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        if interaction.message is None or interaction.message.interaction.user.id != interaction.user.id:  # type: ignore
            return
        self.sview.stop()
        await del_msg(interaction.message, interaction.user)


class DView(View):
    def __init__(self, timeout=300) -> None:
        self.msg = None
        super().__init__(timeout=timeout)
        self.add_item(EnvelopeButton())
        self.add_item(CrossButton(self))

    async def on_timeout(self) -> None:
        self.clear_items()
        self.add_item(Button(label="Please use reactions ✉️ 🗑️", disabled=True))
        await self.msg.edit(view=self)  # type: ignore


bot = Bot()
cgpt = OA.ChatGPT(str(OPENAI_TOKEN))


def check_sfw(channel_id) -> bool:
    if channel_id in sfw_channels:
        return True
    else:
        return False


async def send_dm(msg: discord.Message, usr: discord.User | discord.Member) -> None:
    log.info(f"{usr} requested DM of: {msg.id}")

    for att in msg.attachments:
        await usr.send(att.url)

    for emb in msg.embeds:
        if emb.image and emb.image.url:
            await usr.send(emb.image.url)
        elif emb.url:
            await usr.send(emb.url)

    log.info(f"DM sent to {usr}.")


async def del_msg(msg: discord.Message, requester: discord.User | discord.Member) -> None:
    if msg.content.startswith("Deleted"):
        return

    log.info(f"{requester} requested DELETION of: {msg.id}")

    await msg.edit(
        content=f"Deleted on the request from **{requester}**",
        embeds=[],
        attachments=[],
        view=None,
    )

    log.info(f"{msg.id} DELETED")


async def lora_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    *other, current = current.strip().lower().split() or [""]
    if not current and not other:
        return SD.LORALIST[:25]

    return [
        app_commands.Choice(name=f'{" ".join(other or [current])} {text.name}'[:100], value=f'{" ".join(other or[current])} {text.value}'[:100][:100])
        for text in islice(
            sorted(
                SD.LORALIST,
                key=lambda x: CSequenceMatcher(None, x.value, current).quick_ratio(),
                reverse=True,
            ),
            25,
        )
    ]


@bot.tree.error
async def cooldown_error(interaction: discord.Interaction, error) -> None:
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(content=f"Try again in {round(error.retry_after)} seconds.", ephemeral=True)


@bot.event
async def on_ready() -> None:
    log.info(f"Logged in as {bot.user}")
    await bot.tree.set_translator(MyTranslator())


@bot.tree.command(name="image", description=ls("Request image from DALL-E"))
@app_commands.describe(prompt=ls("Image prompt"), resolution=ls("Resolution X*X pixels"))
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def image(ctx: discord.Interaction, prompt: str, resolution: OA.resolutions) -> None:
    """
    Request image from OpenAI DALL-E
    """

    view = DView()
    log.info(f"DALL-E image requested by {ctx.user} in {ctx.channel} {ctx.channel_id}: {prompt}")
    await ctx.response.defer()
    try:
        image_url = await cgpt.generate_image(prompt=prompt, resolution=resolution)
        await SD.logimage(image_url)
        log.info(f'DALL-E image saved: {f"images/{SD.dt_os()}_image.png"}')
        view.msg = await ctx.followup.send(content=image_url, view=view)
    except OA.InvalidRequest:
        await ctx.followup.send("InvalidRequest. Probably safety filters")
    except Exception:
        await ctx.followup.send("Unknown exception.")


@bot.tree.command(
    name="sdimage",
    description=ls("Request image from Stable Diffusion (may not be available)"),
)
@app_commands.autocomplete(loras=lora_autocomplete)
@app_commands.describe(
    prompt=ls("Image prompt"),
    height=ls("Vertical resolution in pixels"),
    width=ls("Horizontal resolution in pixels"),
    loras=ls("LoRas"),
    negative=ls("Negative prompt"),
)
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def sdimage(
    ctx: discord.Interaction,
    prompt: str,
    height: SD.resolutions,
    width: SD.resolutions,
    loras: str | None,
    negative: str | None,
) -> None:
    """
    Request image from Stable Diffusion (may not be available)
    """
    await ctx.response.defer()
    sfw = check_sfw(ctx.channel_id)

    prompt_f = f"{SD.clean_prompt(prompt, sfw)} {loras or ''}".rstrip()
    log.info(f"SD image requested by {ctx.user} in {ctx.channel} {ctx.channel_id} : {prompt_f}")
    view = DView()
    if await SD.checksd():
        try:
            files = await SD.txt2img(prompt_f, int(height), int(width), str(negative or ""), sfw)
            log.info(f'SD image saved: {", ".join(files)}')
            view.msg = await ctx.followup.send(
                content=f"**PROMPT**: *{prompt_f}*",
                files=[discord.File(file) for file in files],
                view=view,
            )
        except Exception as e:
            log.warning(str(e))
            await ctx.followup.send(str(e))
    else:
        await ctx.followup.send("SD offline! Try DALL-E **/image** instead.")
        log.warning("SD unavailable!")
        return


@bot.tree.command(
    name="img2img",
    description="Request image from Stable Diffusion (may not be available)",
)
@app_commands.describe(
    prompt=ls("Image prompt"),
    negative=ls("Negative prompt"),
    height=ls("Vertical resolution in pixels"),
    width=ls("Horizontal resolution in pixels"),
    denoising=ls("Denoising value 0 - 1 with 0.05 increments"),
    image_url=ls("URL for img2img image"),
)
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def sdimg2img(
    ctx: discord.Interaction,
    prompt: str,
    negative: str,
    height: SD.resolutions,
    width: SD.resolutions,
    denoising: float,
    image_url: str,
) -> None:
    """
    Request an image-to-image generation from Stable Diffusion.
    """

    view = DView()
    log.info(f"SD i2i image requested by {ctx.user} in {ctx.channel} {ctx.channel_id} : {prompt}")
    await ctx.response.defer()
    if not await SD.checksd():
        await ctx.followup.send("SD offline! Try DALL-E **/image** instead.")
        log.warning("SD unavailable!")
        return
    try:
        files = await SD.img2img(
            prompt,
            int(height),
            int(width),
            denoising,
            image_url,
            negative,
            check_sfw(ctx.channel_id),
        )
        log.info(f'SD image saved: {", ".join(files)}')
        view.msg = await ctx.followup.send(files=[discord.File(file) for file in files], view=view)
    except SD.ImgNotFound:
        await ctx.followup.send(f"Image not found! URL provided: {image_url}")
        log.info("Image not found")
    except SD.ImgTooLarge:
        await ctx.followup.send("Image too large! Max 1MB")
        log.info("Image too large")
    except SD.SDTimeout:
        await ctx.followup.send("SD timed out!")
        log.warning("SD TIMED OUT")
    except Exception as e:
        log.warning(f"Unknown exception {e.__class__.__name__}")
        await ctx.followup.send(str(e))


@bot.tree.command(name="chat", description=ls("Request chat completion from OpenAI ChatGPT"))
@app_commands.describe(text=ls("Your message to ChatGPT"))
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
async def chat(ctx: discord.Interaction, text: str) -> None:
    """
    Request chat completion from OpenAI ChatGPT
    """
    if ctx.channel_id is None:
        return

    tag = None
    sent = False
    text = text[:200]

    log.info(f"{ctx.user} asked in {ctx.channel} {ctx.channel_id}: {text}")

    await ctx.response.defer()
    replied = await cgpt.chat_completion(ConversationLog(user_id=ctx.user.id, user_handle=str(ctx.user), role="user", content=text), convo_id=ctx.channel_id)

    result = f"**{ctx.user}**: {text}\n**{bot.user}**: "
    channel = ctx.channel
    if not isinstance(channel, (discord.TextChannel)):
        return

    if len(result) + len(replied) < 1900:
        # print("OK. SHORT ENOUGH")
        await ctx.followup.send(content=result + replied, silent=False)
        result = ""
        log.info(f"ChatGPT reply in {ctx.channel} {ctx.channel_id} : {replied}")
        return

    def split_iter(text: str) -> Generator[str, None, None]:
        """Splits oversized strings"""

        for line in text.splitlines():
            if (lenline := len(line)) > MAX_MSG_LEN:
                for i in range(0, lenline, MAX_MSG_LEN):
                    yield line[i : i + MAX_MSG_LEN]
            else:
                yield line

    for line in split_iter(replied):
        print(repr(result))
        if len(result) + len(line) < MAX_MSG_LEN:
            result += line + "\n"
            print(len(result))
            continue

        if len(matches := re.findall(r"```(?:(\w+)\b(?>\n))?", result)) % 2 == 1:
            tag = matches[-1]
            result += "```"

            if not sent:
                await ctx.followup.send(result)
                sent = True
            else:
                await channel.send(result)

            result = f"```{tag}\n{line}"

        else:
            if not sent:
                await ctx.followup.send(result)
                sent = True
            else:
                await channel.send(result)

            result = line
    print("SECOND", repr(result))

    if len(result) > 0 and result != f"```{tag}\n" and result != f"```{tag}\n```\n":
        if result.count("```") % 2 == 1:
            result += "```"

        if not sent:
            await ctx.followup.send(result)
        else:
            await channel.send(result)
    print(type(replied))
    log.info(f"ChatGPT reply in {ctx.channel} {ctx.channel_id} : {replied}")


@bot.tree.command(name="upscale", description="Request upscale")
@app_commands.describe(image_url="Image URL", factor="Upscale factor 1x-4x", upscaler="Upscaler")
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
async def upscale(
    ctx: discord.Interaction,
    image_url: str,
    factor: float | None,
    upscaler: SD.upscalers | None,
) -> None:
    if factor is None:
        factor = 2
    if upscaler is None:
        upscaler = "R-ESRGAN 4x+ Anime6B"

    log.info(f"Upscale requested by {ctx.user} in {ctx.channel} {ctx.channel_id}")
    await ctx.response.defer()
    try:
        image_f = await SD.upscale(image_url, factor, upscaler)
        log.info(f"Upscaled image saved: {image_f}")
        await ctx.followup.send(file=discord.File(image_f))
    except Exception as e:
        log.warning(e.__class__.__name__)
        await ctx.followup.send(e.__class__.__name__)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    if (
        not isinstance(ch := bot.get_channel(payload.channel_id), discord.TextChannel)
        or (msg := await ch.fetch_message(payload.message_id)).author != bot.user
        or (usr := bot.get_user(payload.user_id)) is None
    ):
        return

    if payload.emoji.name == "✉️":
        await send_dm(msg, usr)

    if payload.emoji.name == "🗑️" or payload.emoji.name == "❌":
        if msg.interaction.user.id != usr.id:  # type: ignore
            return
        await del_msg(msg, usr)


@bot.hybrid_command(hidden=True)
async def synchronise(ctx: commands.Context) -> None:
    """
    sync commands
    """
    if ctx.author.id not in users_allowed_to_sync or ctx.guild is None:
        return
    print(f"sync requested in {ctx.guild}")
    await ctx.defer(ephemeral=True)
    SD.refresh_loras()
    bot.tree.copy_global_to(guild=ctx.guild)
    comms = await bot.tree.sync(guild=ctx.guild)
    await ctx.reply(f"SYNCED {comms}", ephemeral=True)


if __name__ == "__main__" and DISCORD_TOKEN is not None:
    import subprocess

    subprocess.Popen(["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "7859"])
    subprocess.Popen(["python", "gr_interface.py"])
    bot.run(str(DISCORD_TOKEN))
