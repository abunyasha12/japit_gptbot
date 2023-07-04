import discord
import pandas
from discord import app_commands
from discord.app_commands import TranslationContextLocation as CL


class MyTranslator(app_commands.Translator):
    """Класс переводчика для автопревода"""

    def __init__(self):
        self.df = pandas.read_csv("ru_RU.csv")

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> str | None:
        text = str(string)
        loc = context.location
        if (
            loc
            == CL.choice_name
            # or loc == CL.parameter_name
            # or loc == CL.command_name
        ):
            return text
        if locale == discord.Locale.russian:
            try:
                idx = self.df[self.df["original"] == text].index[0]
                tlation = str(self.df.at[idx, "ru_RU"])
                return tlation
            except IndexError:
                print(f"COULD NOT TRANSLATE TO RUSSIAN: '{text}' NOT FOUND IN ru_RU.csv")
                return text
        else:
            return text
