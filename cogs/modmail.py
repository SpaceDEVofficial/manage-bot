import asyncio
import datetime
import os
import platform
import time

import discord
from PycordPaginator import Paginator
from discord.ext.commands import command, Cog
from pycord_components import (
    Button,
    ButtonStyle,
    Select,
    SelectOption,
)
from antispam import AntiSpamHandler
from antispam.ext import AntiSpamTracker

class modmail(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dict = {
            "892557938554699777":"📧 일반 문의",
            "892558109770412042":"👮‍♂️ 신고 문의",
            "892558436800290817":"🙌 팀 지원 문의"
        }
        self.bot.handler = AntiSpamHandler(self.bot, no_punish=True)
        self.bot.tracker = AntiSpamTracker(self.bot.handler,
                                      3)  # 3 Being how many 'punishment requests' before is_spamming returns True
        self.bot.handler.register_extension(self.bot.tracker)

    @Cog.listener()
    async def on_message(self,message:discord.Message):
        await self.bot.handler.propagate(message)

        if self.bot.tracker.is_spamming(message):
            target = message.author
            reason = "스팸 행위로 인한 경고"
            cur = await self.bot.db_con.execute("SELECT * FROM warn_list WHERE user_id = ?", (target.id,))
            datas = await cur.fetchall()
            print(datas)
            if datas == []:
                end = datetime.datetime.utcnow() + datetime.timedelta(days=3)
                end = end.strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "🔇 3일 뮤트"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                              (target.id, reason, end, timestamp))
            elif len(datas) == 1:
                end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                end = end.strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "🔇 7일 뮤트"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                              (target.id, reason, end, timestamp))
            else:
                end = "2100-12-31 23:59"
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "🔇 영구 뮤트"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                              (target.id, reason, end, timestamp))
            await self.bot.db_con.execute("INSERT INTO warn_list(user_id,reason,stamp) VALUES (?,?,?)",
                                          (target.id, reason + " " + punish, timestamp))
            await self.bot.db_con.commit()
            await cur.close()
            guild = message.guild
            mutedRole = discord.utils.get(guild.roles, name="Muted")

            if not mutedRole:
                mutedRole = await guild.create_role(name="Muted")
                channels = guild.channels
                for channel in channels:
                    await channel.set_permissions(mutedRole, speak=False, send_messages=False)
            await target.add_roles(mutedRole, reason=reason)
            em = discord.Embed(
                title="경고가 부여됨",
                description="👮‍♂️ 부여자 - {admin}\n📌 부여대상 - {user}\n\n❔ 사유 - `{reason}`\n\n 처벌내용 - {punish}".format(
                    admin=self.bot.user.mention, user=target.mention, reason=reason, punish=punish),
                timestamp=datetime.datetime.now(),
                color=discord.Color.red()
            )
            wem = discord.Embed(
                title="경고가 부여되었습니다!",
                description="👮‍♂️ 부여자 - {admin}\n📌 부여대상 - {user}\n\n❔ 사유 - `{reason}`\n\n 처벌내용 - {punish}".format(
                    admin=self.bot.user.mention, user=target.mention, reason="스팸 행위(맨션도배 또는 일방적 도배)로 인한 경고", punish=punish),
                timestamp=datetime.datetime.now(),
                color=discord.Color.red()
            )
            await message.channel.send(content=f"{message.author.mention}, 스팸행위를 멈추어주세요! \n스팸행위로 인해 경고가 부여되었습니다!",embed=wem)
            await self.bot.get_channel(884219305942740992).send(embed=em)
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel)and message.author != self.bot.user:
            cates = [892557938554699777,892558109770412042,892558436800290817]
            for i in cates:
                for chs in self.bot.get_channel(i).channels:
                    if chs.topic == str(message.author.id):
                        if len(message.attachments) != 0:
                            for i in message.attachments:
                                await self.bot.get_channel(int(chs.id)).send(i.url)
                        await self.bot.get_channel(int(chs.id)).send(message.content)
                        await message.add_reaction("✅")
                        return
            msg = await message.reply(
                "문의 하시려는 카테고리가 무엇인가요?",
                components=[
                    Select(
                        placeholder="Select",
                        options=[
                            SelectOption(label="일반 문의", value="892557938554699777", description="일반적인 문의(기타포함)를 합니다.",emoji="📧"),
                            SelectOption(label="신고 문의", value="892558109770412042", description="유저신고 및 긴급한 신고를 합니다.",
                                         emoji="👮‍♂️"),
                            SelectOption(label="팀 지원 문의", value="892558436800290817", description="팀원 지원에 대한 문의를 합니다.",
                                         emoji="🙌")
                        ],
                    ),
                ],
            )
            try:
                interaction = await self.bot.wait_for("select_option", check=lambda
                    i: i.user.id == message.author.id and i.message.id == msg.id, timeout=60)
                value = interaction.values[0]
                label = self.dict[value]
                # stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
            except asyncio.TimeoutError:
                await msg.edit("시간이 초과되어 문의가 취소되었습니다.",components=[])
                return
            await msg.edit("문의 카테고리: `{}`".format(label),components=[])
            ch = await self.bot.get_channel(int(value)).create_text_channel(name=str(message.author))
            await ch.edit(topic=str(message.author.id))
            if len(message.attachments) != 0:
                for i in message.attachments:
                    await ch.send(i.url)
            else:
                pass
            await ch.send(str(message.author) +": "+message.content)
            await message.reply("성공적으로 문의 티켓을 개설 및 전달하였습니다.")
        else:
            ch_id = message.channel.topic
            user = await self.bot.fetch_user(str(ch_id))
            if message.content == "s.종료":
                await user.send("관리자가 티켓을 종료하였습니다.\n추가적인 문의가 있으시다면 언제나 문의주십시요\n\n이 메세지에 답변하지 마세요.")
                await message.channel.delete()
                return
            await user.send(f"{message.author.name}: {message.content}")
            await message.add_reaction("✅")




def setup(bot):
    bot.add_cog(modmail(bot))