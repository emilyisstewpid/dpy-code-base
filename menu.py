import asyncio

import discord
from discord.ext import commands

from typing import Union, List, Generator, Callable, Awaitable


class Menu:
    def __init__(self, ctx: commands.Context, embed: discord.Embed, custom_back=None):
        self.ctx = ctx

        self.bot: commands.Bot = ctx.bot
        self.user = ctx.author

        self.higher: Union[Menu, None] = None
        self.lower: List[Menu] = []

        self.embed = embed
        self.description = None
        self.emoji = None
        self.back = getattr(self.higher, "back", None) or str(custom_back) if custom_back else None or "◀"

        self._func = None
        self._func_args = tuple()
        self._func_kwargs = dict()


    @property
    def lower_emojis(self) -> Generator:
        return (menu.emoji for menu in self.lower)


    def set_lower(self, emoji, embed: discord.Embed, description=None):
        if not description:
            if not str(embed.title) == 'Embed.Empty':
                description = embed.title
            else:
                raise ValueError("Missing description or embed.title")

        if str(emoji) in self.lower_emojis or str(emoji) == self.back:
            raise ValueError("Duplicate Emojis")

        lower_menu = Menu(self.ctx, embed)

        lower_menu.description = description
        lower_menu.emoji = str(emoji)
        lower_menu.higher = self


        self.lower.append(lower_menu)
        return lower_menu


    def set_func(self, _func: Union[Callable, Awaitable], *args, **kwargs):
        self._func = _func
        self._func_args = args
        self._func_kwargs = kwargs


    def from_emoji(self, emoji: discord.Emoji):
        try:
            return list(menu for menu in self.lower if menu.emoji == emoji)[0]
        except IndexError:
            return None


    async def send(self, destination: Union[discord.TextChannel, discord.Message]):
        embed = self.embed.copy()
        embed.description = (str(embed.description) if not str(embed.description) == "Embed.Empty" else "") + "\n\n" + "\n".join(f"{menu.emoji}: {menu.description}" for menu in self.lower)

        if isinstance(destination, discord.Message):
            await destination.edit(embed=embed)
            message = destination
        else:
            message = await destination.send(embed=embed)

        def check(r: discord.Reaction, u: discord.User):
            correct_message = r.message.id == message.id
            correct_user = u.id == self.user.id
            valid_emoji = str(r.emoji) in self.lower_emojis or str(r.emoji) == self.back

            return correct_message and correct_user and valid_emoji


        await message.add_reaction(self.back)

        for emoji in self.lower_emojis:
            await message.add_reaction(emoji)

        reaction, user = await self.bot.wait_for('reaction_add', check=check)

        await message.clear_reactions()

        if str(reaction) == self.back:
            if self.higher:
                await self.higher.send(message)
            else:
                await message.delete()
            return

        return await self.from_emoji(reaction.emoji).trigger(message)


    async def trigger(self, message):
        if self._func:
            if asyncio.iscoroutinefunction(self._func):
                return await self._func(*self._func_args, **self._func_kwargs)
            elif asyncio.iscoroutine(self._func):
                return await self._func
            else:
                return self._func(*self._func_args, **self._func_kwargs)
        else:
            return await self.send(message)
