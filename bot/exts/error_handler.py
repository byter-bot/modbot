import io
import traceback

import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(
            embed=discord.Embed(
                color=0xfa5050,
                title='Error!',
                description=f'```{error!r}```'[:1800]
            )
        )

        if hasattr(error, 'original'):
            tb = traceback.format_exception(type(error), error, error.__traceback__)

            await self.bot.get_channel(self.bot.config['mail_channel']).send(
                file=discord.File(io.StringIO('\n'.join(tb)), 'traceback.txt')
            )


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
