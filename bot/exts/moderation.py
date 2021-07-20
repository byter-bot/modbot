import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild: discord.Guild = None
        self.mute_role: discord.Role = None
        if bot.is_ready():
            self.guild = bot.get_guild(bot.config['main_guild'])
            self.mute_role = discord.utils.get(self.guild.roles, name='Muted')

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(self.bot.config['main_guild'])
        self.mute_role = discord.utils.get(self.guild.roles, name='Muted')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.mute_role in message.author.roles:
            await message.delete()

    @commands.command()
    @commands.has_any_role('Créu Crew', 'Créu Curator', 'Créu Captain', 'Créu Connoisseur')
    async def mute(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if self.mute_role in user.roles:
            await ctx.send('User is already muted')
            return

        if ctx.author.top_role <= user.top_role:
            await ctx.send("You don't have permission to mute this person")
            return

        await user.add_roles(self.mute_role, reason=reason)
        await ctx.message.add_reaction('\N{white heavy check mark}')

    @commands.command()
    @commands.has_any_role('Créu Crew', 'Créu Curator', 'Créu Captain', 'Créu Connoisseur')
    async def unmute(self, ctx: commands.Context, user: discord.Member, *, reason: str = None):
        if self.mute_role not in user.roles:
            await ctx.send("User isn't muted")
            return

        if ctx.author.top_role <= user.top_role:
            await ctx.send("You don't have permission to unmute this person")
            return

        await user.remove_roles(self.mute_role, reason=reason)
        await ctx.message.add_reaction('\N{white heavy check mark}')


def setup(bot):
    bot.add_cog(Moderation(bot))
