import os
from pathlib import Path
from datetime import datetime
import logging

from dotenv import load_dotenv

import discord
from discord.ext import commands
import json

import help
from menu import Menu


load_dotenv(".env")

logging.basicConfig(level=logging.INFO)


intents = discord.Intents.default()


def getPre(bot, message):
    if not message.guild:
        return commands.when_mentioned_or("!")(bot, message)

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or("!", "! ")(bot, message)

    prefix = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(prefix, prefix + " ")(bot, message)


bot = commands.Bot(command_prefix=getPre, intents=intents, case_insensitive=True,
                      help_command=help.HelpCommand(show_hidden=False),
                      description="Bot description")


@bot.event
async def on_ready():
    print('---------------------------')
    print(datetime.now())
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('---------------------------')

    game = discord.Game("")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.command(aliases=["setP", "p"])
@commands.has_guild_permissions(manage_guild=True)
async def setPrefix(ctx, *, prefix):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix
        await ctx.send(f'Prefix set to "{prefix}"')

        with open("prefixes.json", "w") as w:
            json.dump(prefixes, w, indent=4)


def extensions():
    files = Path("cogs").rglob("*.py")
    for file in files:
        yield file.as_posix()[:-3].replace("/", ".")


for ext_file in extensions():
    try:
        bot.load_extension(ext_file)
        print(f"Loaded {ext_file}")
    except Exception as ex:
        print(f"Failed to load {ext_file}: {ex}")


bot.run(os.getenv("TOKEN"))
