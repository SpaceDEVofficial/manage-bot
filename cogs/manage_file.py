import io
import asyncio
import discord
from discord.ext import commands


class manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn")
    async def warn(self,ctx:commands.Context,target:discord.Member,reason="No reason"):
        """view = Confirm(user=ctx.author)
        await ctx.send("Do you want to continue?", view=view)
        await view.wait()
        if view.value is None:
            view.clear_items()
            await ctx.reply("Time out!")
        elif view.value:
            view.clear_items()
            await ctx.reply("give warn to `{}`".format(target))
        else:
            await ctx.reply("canceled!")"""
        await ctx.send(".")

def setup(bot):
    bot.add_cog(manage(bot))
