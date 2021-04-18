import discord
from discord.ext import commands, tasks
import json

import secret
import cogs.help


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


client = commands.Bot(command_prefix=getPre, intents=intents, case_insensitive=True, help_command=cogs.help.HelpCommand(show_hidden=False),
                      description="Bot description")


@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------')

    game = discord.Game("")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.command(aliases=["setP", "p"])
@commands.has_guild_permissions(manage_guild=True)
async def setPrefix(ctx, *, prefix):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix
        await ctx.send(f'Prefix set to "{prefix}"')

        with open("prefixes.json", "w") as w:
            json.dump(prefixes, w, indent=4)


initial_extensions = (
    
)

for extension in initial_extensions:
    client.load_extension(extension)

client.run(secret.token)
