import asyncio
import datetime
import time

import discord
#from tools.PagiNation import Paginator
from PycordPaginator import Paginator
from discord.ext.commands import command, Cog
import discord.ext.commands as commands
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
    @commands.has_role('Mod')
    async def warn(self, ctx,target:discord.Member,reason="No Reason"):
        msg = await ctx.reply(
            "정말로 `{user}`에게 경고를 부여할까요?".format(user=target),
            components=[
                Button(label="Confirm",custom_id="yes",style=1),
                Button(label="Cancel",custom_id="no",style=4)
            ]
        )
        try:
            interaction = await self.bot.wait_for("button_click", check=lambda i: i.user.id == ctx.author.id and i.message.id == msg.id,timeout=30)
            name = interaction.custom_id
        except asyncio.TimeoutError:
            await msg.delete()
            return
        if name == "yes":
            cur = await self.bot.db_con.execute("SELECT * FROM warn_list WHERE user_id = ?",(target.id,))
            datas = await cur.fetchall()
            print(datas)
            if datas == []:
                end = datetime.datetime.utcnow() + datetime.timedelta(days=3)
                end = end.strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "🔇 3일 뮤트"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)", (target.id, reason,end,timestamp))
            elif len(datas) == 1:
                end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                end = end.strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "🔇 7일 뮤트"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)", (target.id, reason,end,timestamp))
            else:
                end = "2100-12-31 23:59"
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "🔇 영구 뮤트"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                              (target.id, reason, end,timestamp))
            await self.bot.db_con.execute("INSERT INTO warn_list(user_id,reason) VALUES (?,?)", (target.id, reason +" " +punish))
            await self.bot.db_con.commit()
            await cur.close()
            guild = ctx.guild
            mutedRole = discord.utils.get(guild.roles, name="Muted")

            if not mutedRole:
                mutedRole = await guild.create_role(name="Muted")
                channels = guild.channels
                for channel in channels:
                    await channel.set_permissions(mutedRole, speak=False, send_messages=False)
            await target.add_roles(mutedRole, reason=reason)
            em = discord.Embed(
                title="경고가 부여됨",
                description="👮‍♂️ 부여자 - {admin}\n📌 부여대상 - {user}\n\n❔ 사유 - `{reason}`\n\n 처벌내용 - {punish}".format(admin=ctx.author.mention,user=target.mention,reason=reason,punish=punish),
                timestamp=datetime.datetime.now(),
                color=discord.Color.red()
            )
            await msg.edit(
                content=f"✅ 경고를 부여하였습니다.",
                embed=em,
                components=[Button(label="Confirmed",style=1,disabled=True)]
            )
            await self.bot.get_channel(884219305942740992).send(embed=em)
        else:
            await msg.edit(
                content=f"❎ 취소하였습니다.",
                components=[Button(label="Canceled", custom_id="no", style=4, disabled=True)]
            )

    @command()
    @commands.has_role('Mod')
    async def unwarn(self,ctx,target:discord.Member,reason="No reason"):
        cur = await self.bot.db_con.execute("SELECT * FROM warn_list WHERE user_id = ?",(target.id,))
        datas = await cur.fetchall()
        if datas == []:
            await ctx.reply("This user have not warn datas!")
            return
        msg = await ctx.reply(
            "** **",
            components=[
                    Select(
                        placeholder="Select",
                        options=[
                            SelectOption(label=target.display_name, value=i[2],description="경고사유 - {}".format(i[1])) for i in datas
                        ],
                    ),
            ],
        )
        try:
            interaction = await self.bot.wait_for("select_option", check=lambda i: i.user.id == ctx.author.id and i.message.id == msg.id,timeout=30)
            value = interaction.values[0]
            stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
        except asyncio.TimeoutError:
            await msg.delete()
            return
        await self.bot.db_con.execute("DELETE FROM warn_list WHERE user_id = ? AND dates = ?",(target.id,value))
        await self.bot.db_con.execute("DELETE FROM mute_list WHERE user_id = ? AND stamp = ?", (target.id, stamp))
        await self.bot.db_con.commit()
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")
        await target.remove_roles(mutedRole)
        em = discord.Embed(
            title="경고가 취소됨",
            description="👮‍♂️ 경고취소자 - {admin}\n📌 대상 - {user}\n\n❔ 사유 - `{reason}`".format(
                admin=ctx.author.mention, user=target.mention, reason=reason),
            timestamp=datetime.datetime.now(),
            color=discord.Color.green()
        )
        await msg.edit("✅ SUCCESS!",embed=em,components=[])
        await self.bot.get_channel(884219305942740992).send(embed=em)


def setup(bot):
    bot.add_cog(manage(bot))