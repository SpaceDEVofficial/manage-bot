import discord
from tools.PagiNation import Paginator
from discord.ext.commands import command, Cog
from pycord_components import (
    Button,
    ButtonStyle,
    Select,
    SelectOption,
)


class ExampleCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def button(self, ctx):
        msg = await ctx.send(
            "Hello, World!",
            components=[
                Button(label="WOW button!"),
                Button(label="NOW button!")
            ]
        )
        interaction = await self.bot.wait_for("button_click", check=lambda i: i.component.label.startswith("WOW"))
        await msg.edit(
            content=f"You clicked {interaction.component.label}",
            components=[]
        )
        await interaction.send(content="Button clicked!")

    @command()
    async def select(self, ctx):
        async def callback(interaction):
            await interaction.send(content=interaction.values)

        await ctx.send(
            "Select callbacks!",
            components=[
                self.bot.components_manager.add_callback(
                    Select(
                        options=[
                            SelectOption(label="a", value="a"),
                            SelectOption(label="b", value="b"),
                        ],
                    ),
                    callback,
                )
            ],
        )

    @command()
    async def test(self,ctx):
        #embeds = ["1","2","3","4"]
        embeds = [discord.Embed(title="1 page"), discord.Embed(title="2 page"), discord.Embed(title="3 page"),
                  discord.Embed(title="4 page"), discord.Embed(title="5 page")]
        desc = {
            "기본 도움말":"기본적인 도움말임",
            "서버관리 도움말":"서버관리 도움말임",
            "뮤직 도움말":"노래 도움말임",
            "경제 도움말":"경제 도움말임",
            "기타 도움말":"기타 도움말임"
        }


        e = Paginator(client=self.bot.components_manager,embeds=embeds,channel=ctx.channel,only=ctx.author,ctx=ctx,use_select=True,desc=desc)
        await e.start()

def setup(bot):
    bot.add_cog(ExampleCog(bot))