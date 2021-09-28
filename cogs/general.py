import asyncio
import os
import platform
import discord
from PycordPaginator import Paginator
from discord.ext.commands import command, Cog
from pycord_components import (
    Button,
    ButtonStyle,
    Select,
    SelectOption,
)
class manage(Cog):
    def __init__(self, bot):
        self.bot = bot


    @command()
    async def help(self,ctx):
        main = discord.Embed(title="메인페이지",
                            description="1페이지 - 서버관리\n2페이지 - 기본",
                             colour=discord.Colour.blue()
                            )
        guild = ctx.guild
        mod = discord.utils.get(guild.roles, name="Mod")
        manage = discord.Embed(title="1페이지( 서버관리 )",
                            description="• s.warn @user reason(Option)\n• s.unwarn @user reason(Option) \n\nThis command require {} role".format(mod.mention),
                             colour=discord.Colour.blue()
                            )

        #temp = ["•","•","•","•","•","•","•","•"]
        gen = ["• s.serverinfo", "• s.botinfo","• s.invite"]
        general = discord.Embed(
            title="2페이지( 기본 )",
            description="\n".join(gen),
            colour=discord.Colour.blue()
        )

        embeds = [main,manage,general]
        desc = {
            "메인 페이지":"목차가 포함된 메인페이지입니다.",
            "서버관리 도움말":"서버관리 도움말입니다.",
            "기본 도움말": "기본 도움말입니다."
        }


        e = Paginator(client=self.bot.components_manager,embeds=embeds,channel=ctx.channel,only=ctx.author,ctx=ctx,use_select=True,desc=desc)
        await e.start()

    @command()
    async def botinfo(self, ctx):
        """
        Get some useful (or not) information about the bot.
        """

        # This is, for now, only temporary

        embed = discord.Embed(
            description="SpaceDEV Manage bot Info",
            color=0x42F56C
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="gawi#9537",
            inline=True
        )
        embed.add_field(
            name="Pycord Version:",
            value=f"{discord.__version__}",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=False
        )
        embed.add_field(
            name="OS Platform:",
            value=f"{platform.platform()}",
            inline=False
        )
        embed.add_field(
            name="Prefix:",
            value=f"s.",
            inline=True
        )
        embed.add_field(
            name="Ping:",
            value=str(round(self.bot.latency * 1000)) + "ms",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )
        await ctx.reply(embed=embed)

    @command()
    async def serverinfo(self,ctx):
        server = ctx.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{server}",
            color=0x42F56C
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="Server ID",
            value=server.id
        )
        embed.add_field(
            name="Member Count",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{channels}"
        )
        embed.add_field(
            name=f"Roles ({role_length})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {time}"
        )
        await ctx.reply(embed=embed)

    @command()
    async def invite(self,ctx):
        bots = {
            "태시아 봇":"https://shrt.kro.kr/태시아",
            "GPROM":"https://discord.com/api/oauth2/authorize?client_id=850259629316505650&permissions=8&scope=bot",
            "Konosuba":"https://shrt.kro.kr/konosuba",
            "PUBG Live":"https://shrt.kro.kr/pubglive",
            "lia":"https://lia.vfnets.com/invite"
        }
        bots_desc = {
            "태시아 봇" : "서버관리가 주목적이며 부가적으로 주식기능도 있습니다!",
            "GPROM": "서로에게 이득이 되는 좋은 홍보봇.",
            "Konosuba":"넥슨의 '코노스바 모바일 판타스틱 데이즈'를 디스코드에서 만나보세요.",
            "PUBG Live":"배틀그라운드 매치가 끝날때마다 해당 매치의 결과를 분석하여 실시간으로 알려드립니다.",
            "lia":"다기능 통합 봇 Lia_"
        }
        msg = await ctx.reply(
            "Which bot do you want to invite?",
            components=[
                Select(
                    placeholder="Select",
                    options=[
                        SelectOption(label=key, value=value, description=bots_desc[key]) for key,value
                        in bots.items()
                    ],
                ),
            ],
        )
        try:
            interaction = await self.bot.wait_for("select_option",
                                                  check=lambda i: i.user.id == ctx.author.id and i.message.id == msg.id,
                                                  timeout=30)
            value = interaction.values[0]
            # stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
        except asyncio.TimeoutError:
            await msg.delete()
            return
        await msg.edit("Here we go!",components=[Button(label="Invite",style=5,url=value)])

def setup(bot):
    bot.add_cog(manage(bot))