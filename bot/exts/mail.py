import datetime
import difflib

import discord
from discord.ext import commands


class Mail(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mail: discord.TextChannel = None
        self.last_dm: discord.User = None

        if bot.is_ready():
            self.mail = bot.get_channel(bot.config['mail_channel'])

    @commands.Cog.listener()
    async def on_ready(self):
        self.mail = self.bot.get_channel(self.bot.config['mail_channel'])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.type == discord.ChannelType.private:
            self.last_dm = message.author

            embed = discord.Embed(
                color=0x5050fa,
                description=message.content,
                timestamp=message.created_at
            )

            embed.set_footer(text=f'Msg ID: {message.id}')
            embed.set_author(
                name=f'{message.author} ({message.author.id})',
                icon_url=message.author.avatar_url
            )

            await self.mail.send(
                embed=embed,
                files=[await i.to_file() for i in message.attachments] or None
            )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.type == discord.ChannelType.private:
            self.last_dm = message.author

            word_diff = difflib.ndiff(
                discord.utils.escape_markdown(before.content).split(' '),
                discord.utils.escape_markdown(message.content).split(' '),
                linejunk=lambda x: not x or x.isspace()
            )
            formatted_edit = ''
            for i in word_diff:
                if i.startswith('-'):
                    formatted_edit += f'~~{i[2:] or " "}~~ '
                elif i.startswith('+'):
                    formatted_edit += f'**{i[2:] or " "}** '
                elif i.startswith(' '):
                    formatted_edit += f'{i[2:] or " "} '

            formatted_edit = formatted_edit.replace('~~ ~~', ' ').replace('** **', ' ')

            embed = discord.Embed(
                color=0xfae060,
                title='Edited message',
                description=formatted_edit
            )

            embed.set_footer(text=f'Msg ID: {message.id}')
            embed.set_author(
                name=f'{message.author} ({message.author.id})',
                icon_url=message.author.avatar_url
            )

            await self.mail.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if payload.cached_message:
            return

        if 'bot' in payload.data and payload.data['bot']:
            return

        data: dict = payload.data
        author: discord.User = self.bot.get_user(int(data['author']['id']))
        channel: discord.TextChannel = await self.bot.fetch_channel(data['channel_id'])
        if channel.type == discord.ChannelType.private:
            embed = discord.Embed(
                color=0xfae060,
                title='Edited message [uncached]',
                description=data['content'],
                timestamp=datetime.datetime.fromisoformat(data['timestamp'])
            )

            embed.set_footer(text=f'Msg ID: {data["id"]}')
            embed.set_author(
                name=f'{author} ({author.id})',
                icon_url=author.avatar_url
            )

            await self.mail.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.type == discord.ChannelType.private:
            embed = discord.Embed(
                color=0xfa5050,
                title='Deleted message',
                description=message.content
            )

            embed.set_footer(text=f'Msg ID: {message.id}')
            embed.set_author(
                name=f'{message.author} ({message.author.id})',
                icon_url=message.author.avatar_url
            )

            await self.mail.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if payload.cached_message:
            return

        channel: discord.TextChannel = await self.bot.fetch_channel(payload.channel_id)
        if channel.type == discord.ChannelType.private:
            embed = discord.Embed(
                color=0xfa5050,
                title='Deleted message [uncached]',
                description='N/A'
            )

            embed.set_footer(text=f'Msg ID: {payload.message_id}')
            embed.set_author(name='???')

            await self.mail.send(embed=embed)

    @commands.command(aliases=['msglast', 'mlast', 'ml'])
    async def messagelast(self, ctx: commands.Context, *, message: str):
        if self.last_dm is None:
            await ctx.send('No last dm!')
            return

        await self.last_dm.send(message)
        await ctx.send(f'Sent message to {self.last_dm} ({self.last_dm.id})')

    @commands.command(aliases=['msg', 'm'])
    async def message(self, ctx: commands.Context, user: discord.User, *, message: str):
        await user.send(message)
        await ctx.send(f'Sent message to {self.last_dm} ({self.last_dm.id})')


def setup(bot):
    bot.add_cog(Mail(bot))
