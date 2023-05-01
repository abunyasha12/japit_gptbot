from datetime import datetime
import discord
import os
from discord.ext import commands
from discord.ui import View, Button
from discord import app_commands
from dotenv import load_dotenv
import requests
import logging
import logging.handlers
import typing
import OA_tools as OA
import SD_tools as SD


log = logging.getLogger()
logging.getLogger("openai").setLevel(logging.ERROR)
log.setLevel(logging.INFO)

fhandler = logging.handlers.TimedRotatingFileHandler(
    "./logs/logfile.log", "D", backupCount=30, encoding="utf-8")
dt_fmt = '%Y-%m-%d %H:%M:%S'
fmt = logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s:%(lineno)d] %(message)s', dt_fmt)
fhandler.setFormatter(fmt)
log.addHandler(fhandler)

chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
chandler.setFormatter(fmt)
log.addHandler(chandler)


load_dotenv()

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
OPENAI_TOKEN = os.environ.get('OPENAI_TOKEN')
DEEPL_TOKEN = os.environ.get('DEEPL_TOKEN')

allowed_channel = [1093166962428882996,  # japit.gpt
                   1093529718277541958,  # japit.gpt_adult
                   831502411411095562  # pg.general
                   ]

guilds_ids = [208894633432973314,  # proving grounds
              333700550862569472  # japit
              ]

sfw_channels = [1093166962428882996,  # japit.gpt
                831502411411095562  # pg.general
                ]

users_allowed_to_sync = [142228355104636928,  # drug
                         264168634123812865  # tiki
                         ]


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guild_reactions = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)


class EnvelopeButton(Button):
    def __init__(self):
        super().__init__(emoji="✉️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.message is None:
            return
        await send_dm(interaction.message, interaction.user)


class CrossButton(Button):
    def __init__(self):
        super().__init__(emoji="🗑️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if (interaction.message is None
                or interaction.message.interaction.user.id != interaction.user.id  # type: ignore
            ):
            return
        await del_msg(interaction.message, interaction.user)


class DView(View):
    def __init__(self, timeout=360) -> None:
        self.msg = None
        super().__init__(timeout=timeout)
        self.add_item(EnvelopeButton())
        self.add_item(CrossButton())

    async def on_timeout(self):
        self.clear_items()
        self.add_item(
            Button(label="Please use reactions ✉️ 🗑️", disabled=True))
        await self.msg.edit(view=self)  # type: ignore


bot = Bot()
cgpt = OA.ChatGPT(OPENAI_TOKEN)


def check_sfw(channel_id) -> bool:
    if channel_id in sfw_channels:
        return True
    else:
        return False


def dt_os() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def logimage(url) -> None:
    response = requests.get(url)
    with open(f"images/{dt_os()}_image.png", "wb") as f:
        f.write(response.content)


async def send_dm(msg: discord.Message, usr: discord.User | discord.Member) -> None:
    log.info(f'{usr} requested DM of: {msg.id}')

    for att in msg.attachments:
        await usr.send(att.url)

    for emb in msg.embeds:
        if emb.image and emb.image.url:
            await usr.send(emb.image.url)
        elif emb.url:
            await usr.send(emb.url)
    log.info(f'DM sent to {usr}.')


async def del_msg(msg: discord.Message, requester: discord.User | discord.Member) -> None:
    if msg.content.startswith("Deleted"):
        return
    log.info(f'{requester} requested DELETION of: {msg.id}')
    await msg.edit(content=f"Deleted on the request from **{requester}**", embeds=[], attachments=[], view=None)
    log.info(f'{msg.id} DELETED')


@bot.event
async def on_command_error(ctx, error) -> None:
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.defer()
        await ctx.reply(f"Try again in {round(error.retry_after, 1)} seconds.")


@bot.tree.error
async def cooldown_error(interaction: discord.Interaction, error) -> None:
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Try again in {round(error.retry_after, 1)} seconds.", ephemeral=True)


@bot.event
async def on_ready() -> None:
    log.info(f'Logged in as {bot.user}')


@bot.tree.command(name="image", description="Request image from DALL-E.")
@app_commands.describe(prompt="Image prompt", resolution="Resolution, X*X pixels")
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def image(ctx: discord.Interaction, prompt: str, resolution: typing.Literal["256", "512"]) -> None:
    '''Request image from OpenAI DALL-E'''
    if ctx.channel_id not in allowed_channel:
        return
    view = DView()
    log.info(
        f'DALL-E image requested by {ctx.user} in {ctx.channel} {ctx.channel_id}: {prompt}')
    await ctx.response.defer()
    try:
        image_url = await cgpt.generate_image(prompt=prompt, resolution=resolution)
        logimage(image_url)
        log.info(f'DALL-E image saved: {f"images/{dt_os()}_image.png"}')
        view.msg = await ctx.followup.send(content=image_url, view=view)
    except OA.InvalidRequest:
        await ctx.followup.send("InvalidRequest. Probably safety filters")
    except Exception:
        await ctx.followup.send("Unknown exception.")


@bot.tree.command(name="sd-image",
                  description="Request image from Stable Diffusion. (may not be available)")
@app_commands.describe(prompt="generation prompt",
                       height="Vertical resolution, pixels",
                       width="Horizontal resolution, pixels")
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def sdimage(ctx: discord.Interaction,
                  prompt: str,
                  height: typing.Literal["448", "512", "640", "704", "768"],
                  width:  typing.Literal["448", "512", "640", "704", "768"]) -> None:
    '''Request image from Stable Diffusion.'''
    if ctx.channel_id not in allowed_channel:
        return
    vert_i = int(height)
    hor_i = int(width)
    log.info(
        f'SD image requested by {ctx.user} in {ctx.channel} {ctx.channel_id} : {prompt}')
    await ctx.response.defer()
    view = DView()
    if await SD.checksd():
        files = await SD.txt2img(prompt, vert_i, hor_i, sfw=check_sfw(ctx.channel_id))
        log.info(f'SD image saved: {", ".join(files)}')
        view.msg = await ctx.followup.send(files=[discord.File(file) for file in files], view=view)
    else:
        await ctx.followup.send('SD offline! Try DALL-E **/image** instead.')
        log.warning("SD unavailable!")
        return


@bot.tree.command(name="sd-advanced",
                  description="Request image from Stable Diffusion. (may not be available)")
@app_commands.describe(prompt="generation prompt",
                       negative_prompt="Negative prompt",
                       height="Vertical resolution, pixels",
                       width="Horizontal resolution, pixels")
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def sdadv(ctx: discord.Interaction,
                prompt: str,
                negative_prompt: str,
                height: typing.Literal["448", "512", "640", "704", "768"],
                width:  typing.Literal["448", "512", "640", "704", "768"]) -> None:
    '''Request image from Stable Diffusion. Advanced mode.'''
    if ctx.channel_id not in allowed_channel:
        return
    vert_i = int(height)
    hor_i = int(width)
    view = DView()
    log.info(
        f'SD image requested by {ctx.user} in {ctx.channel} {ctx.channel_id} : {prompt}')
    await ctx.response.defer()
    if await SD.checksd():
        files = await SD.txt2img(prompt, vert_i, hor_i, negative_prompt, sfw=check_sfw(ctx.channel_id))
        log.info(f'SD image saved: {", ".join(files)}')
        view.msg = await ctx.followup.send(files=[discord.File(file) for file in files], view=view)
    else:
        await ctx.followup.send('SD offline! Try DALL-E **/image** instead.')
        log.warning("SD unavailable!")
        return


@bot.tree.command(name="sd-img2img",
                  description="Request image from Stable Diffusion. (may not be available)")
@app_commands.describe(prompt="generation prompt",
                       negative_prompt="Negative prompt",
                       height="Vertical resolution, pixels",
                       width="Horizontal resolution, pixels",
                       denoising="Denoising value 0 - 1 with 0.05 increments",
                       image_url="URL for img2img image")
@app_commands.guilds(*guilds_ids)
@app_commands.checks.cooldown(1, 120, key=lambda i: (i.guild_id, i.user.id))
async def sdimg2img(ctx: discord.Interaction,
                    prompt: str,
                    negative_prompt: str,
                    height: typing.Literal["448", "512", "640", "704", "768"],
                    width:  typing.Literal["448", "512", "640", "704", "768"],
                    denoising: float,
                    image_url: str) -> None:
    '''Request an image-to-image generation from Stable Diffusion.'''
    if ctx.channel_id not in allowed_channel:
        return
    vert_i = int(height)
    hor_i = int(width)
    view = DView()
    log.info(
        f'SD i2i image requested by {ctx.user} in {ctx.channel} {ctx.channel_id} : {prompt}')
    await ctx.response.defer()
    if await SD.checksd() is not True:
        await ctx.followup.send('SD offline! Try DALL-E **/image** instead.')
        log.warning("SD unavailable!")
        return
    try:
        files = await SD.img2img(prompt, vert_i, hor_i, denoising, image_url, negative_prompt, check_sfw(ctx.channel_id))
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


@bot.command()
async def chat(ctx: commands.Context, *, prompt) -> None:
    ''' Request chat completion from OpenAI ChatGPT'''

    if ctx.channel.id not in allowed_channel:
        return

    log.info(f'{ctx.author} asked in {ctx.channel} {ctx.channel.id}: {prompt}')

    async with ctx.typing():
        replied = False
        text = await cgpt.chat_completion(prompt, ctx.channel.id)
        out = ""
        for line in text.splitlines():
            if len(out) + len(line) < 1997:
                out += line + "\n"
            elif not replied:
                await ctx.reply(content=out)
                replied = True
                out = ""
            else:
                await ctx.send(content=out)
                out = ""
        if len(out) > 0 and not replied:
            await ctx.reply(content=out)
        elif len(out) > 0:
            await ctx.send(content=out)
    log.info(f'ChatGPT reply in {ctx.channel} {ctx.channel.id} : {text}')


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.channel.id not in allowed_channel:
        return

    if message.reference and isinstance((r := message.reference.resolved), discord.Message) and r.author == bot.user and message.author != bot.user:

        ctx = await bot.get_context(message)
        if ((command := bot.get_command('chat')) is None
                and not isinstance(command, commands.Command)):
            return
        async with message.channel.typing():
            await ctx.invoke(command, prompt=message.content)  # type: ignore
        return
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    if (
        payload.channel_id not in allowed_channel
        or not isinstance(ch := bot.get_channel(payload.channel_id), discord.TextChannel)
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


@bot.command(hidden=True)
async def synchronise(ctx: commands.Context) -> None:
    if (ctx.author.id not in users_allowed_to_sync
            or ctx.guild is None
            ):
        return
    print(f"sync requested in {ctx.guild}")
    bot.tree.copy_global_to(guild=ctx.guild)
    comms = await bot.tree.sync(guild=ctx.guild)
    await ctx.reply(f"SYNCED {comms}")


if DISCORD_TOKEN is not None:
    bot.run(DISCORD_TOKEN)
