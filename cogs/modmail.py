import asyncio
import datetime
import os
import platform
import re
import time

import discord
from PycordPaginator import Paginator
from discord.ext.commands import command, Cog
import discord.ext.commands as commands
from pycord_components import (
    Button,
    ButtonStyle,
    Select,
    SelectOption,
)
from antispam import AntiSpamHandler
from antispam.ext import AntiSpamTracker
LINKS = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
INVITE = re.compile(r"(?:https?://)?discord(?:\.com/invite|app\.com/invite|\.gg)/?[a-zA-Z0-9]+/?")
class modmail(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dict = {
            "892557938554699777":"đ§ ěźë° ëŹ¸ě",
            "892558109770412042":"đŽââď¸ ě ęł  ëŹ¸ě",
            "892558436800290817":"đ í ě§ě ëŹ¸ě"
        }
        self.bot.handler = AntiSpamHandler(self.bot, no_punish=True)
        self.bot.tracker = AntiSpamTracker(self.bot.handler,
                                      3)  # 3 Being how many 'punishment requests' before is_spamming returns True
        self.bot.handler.register_extension(self.bot.tracker)
        self.count = []

    @command()
    @commands.has_role('Mod')
    async def uncount(self,ctx):
        if self.count==[]:
            await ctx.reply("empty count!")
            return
        msg = await ctx.reply(
            "** **",
            components=[
                    Select(
                        placeholder="Select",
                        options=[
                            SelectOption(label=self.bot.get_guild(847729860881154078).get_member(i).display_name, value=i) for i in self.count
                        ],
                    ),
            ],
        )
        try:
            interaction = await self.bot.wait_for("select_option", check=lambda i: i.user.id == ctx.author.id and i.message.id == msg.id,timeout=30)
            value = interaction.values[0]
            mem = self.bot.get_guild(847729860881154078).get_member(value)
            #stamp = str(time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
        except asyncio.TimeoutError:
            await msg.delete()
            return
        self.count.remove(value)
        em = discord.Embed(
            title="ěëŠ ę˛˝ęł ę° ěˇ¨ěë¨",
            description="đŽââď¸ ę˛˝ęł ěˇ¨ěě - {admin}\nđ ëě - {user}\n\nâ ěŹě  - `{reason}`".format(
                admin=ctx.author.mention, user=mem.mention, reason="ěëíě§ěě ěëŠ ëë ę´ëŚŹě ěŹë."),
            timestamp=datetime.datetime.now(),
            color=discord.Color.green()
        )
        await msg.edit("â SUCCESS!",embed=em,components=[])
        await self.bot.get_channel(884219305942740992).send(embed=em)

    @Cog.listener()
    async def on_message(self,message:discord.Message):
        await self.bot.handler.propagate(message)

        if self.bot.tracker.is_spamming(message):
            target = message.author
            reason = "ě¤í¸ íěëĄ ě¸í ę˛˝ęł "
            cur = await self.bot.db_con.execute("SELECT * FROM warn_list WHERE user_id = ?", (target.id,))
            datas = await cur.fetchall()
            print(datas)
            if datas == []:
                end = datetime.datetime.utcnow() + datetime.timedelta(days=3)
                end = end.strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "đ 3ěź ëŽ¤í¸"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                              (target.id, reason, end, timestamp))
            elif len(datas) == 1:
                end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                end = end.strftime("%Y-%m-%d %H:%M")
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "đ 7ěź ëŽ¤í¸"
                await self.bot.db_con.execute("INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                              (target.id, reason, end, timestamp))
            else:
                end = "2100-12-31 23:59"
                now = datetime.datetime.utcnow()
                now = now.strftime("%Y-%m-%d %H:%M:%S")
                timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[:-2]
                punish = "đ ěęľŹ ëŽ¤í¸"
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
                title="ę˛˝ęł ę° ëśěŹë¨",
                description="đŽââď¸ ëśěŹě - {admin}\nđ ëśěŹëě - {user}\n\nâ ěŹě  - `{reason}`\n\n ě˛ë˛ë´ěŠ - {punish}".format(
                    admin=self.bot.user.mention, user=target.mention, reason=reason, punish=punish),
                timestamp=datetime.datetime.now(),
                color=discord.Color.red()
            )
            wem = discord.Embed(
                title="ę˛˝ęł ę° ëśěŹëěěľëë¤!",
                description="đŽââď¸ ëśěŹě - {admin}\nđ ëśěŹëě - {user}\n\nâ ěŹě  - `{reason}`\n\n ě˛ë˛ë´ěŠ - {punish}".format(
                    admin=self.bot.user.mention, user=target.mention, reason="ě¤í¸ íě(ë§¨ěëë°° ëë ěźë°Šě  ëë°°)ëĄ ě¸í ę˛˝ęł ", punish=punish),
                timestamp=datetime.datetime.now(),
                color=discord.Color.red()
            )
            await message.channel.send(content=f"{message.author.mention}, ě¤í¸íěëĽź ëŠěśě´ěŁźě¸ě! \ně¤í¸íěëĄ ě¸í´ ę˛˝ęł ę° ëśěŹëěěľëë¤! ěŁźěíě¸ě.",embed=wem)
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
                        await message.add_reaction("â")
                        return
            msg = await message.reply(
                "ëŹ¸ě íěë ¤ë ěš´íęł ëŚŹę° ëŹ´ěě¸ę°ě?",
                components=[
                    Select(
                        placeholder="Select",
                        options=[
                            SelectOption(label="ěźë° ëŹ¸ě", value="892557938554699777", description="ěźë°ě ě¸ ëŹ¸ě(ę¸°ííŹí¨)ëĽź íŠëë¤.",emoji="đ§"),
                            SelectOption(label="ě ęł  ëŹ¸ě", value="892558109770412042", description="ě ě ě ęł  ë° ę¸´ę¸í ě ęł ëĽź íŠëë¤.",
                                         emoji="đŽââď¸"),
                            SelectOption(label="í ě§ě ëŹ¸ě", value="892558436800290817", description="íě ě§ěě ëí ëŹ¸ěëĽź íŠëë¤.",
                                         emoji="đ")
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
                await msg.edit("ěę°ě´ ě´ęłźëě´ ëŹ¸ěę° ěˇ¨ěëěěľëë¤.",components=[])
                return
            await msg.edit("ëŹ¸ě ěš´íęł ëŚŹ: `{}`".format(label),components=[])
            ch = await self.bot.get_channel(int(value)).create_text_channel(name=str(message.author))
            await ch.edit(topic=str(message.author.id))
            if len(message.attachments) != 0:
                for i in message.attachments:
                    await ch.send(i.url)
            else:
                pass
            await ch.send(str(message.author) +": "+message.content)
            await message.reply("ěąęłľě ěźëĄ ëŹ¸ě í°ěźě ę°ě¤ ë° ě ëŹíěěľëë¤.")
        else:
            if message.content == "s.ě˘ëŁ":
                ch_id = message.channel.topic
                user = await self.bot.fetch_user(str(ch_id))
                await user.send("ę´ëŚŹěę° í°ěźě ě˘ëŁíěěľëë¤.\něśę°ě ě¸ ëŹ¸ěę° ěěźěë¤ëŠ´ ě¸ě ë ëŹ¸ěěŁźě­ěě\n\ně´ ëŠě¸ě§ě ëľëłíě§ ë§ě¸ě.")
                await message.channel.delete()
                await user.send(f"{message.author.name}: {message.content}")
                await message.add_reaction("â")
                return
            inv = INVITE.search(message.content)

            if bool(inv):
                if message.channel.topic is None:
                    await message.delete()
                    self.count.append(message.author.id)
                    if self.count.count(message.author.id) <= 2:

                        em = discord.Embed(
                            title="ěëŠ ę°ě§ đ¨",
                            description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\nę˛˝ęł  - {}".format(message.author.mention,self.count.count(message.author.id)),
                            colour=discord.Color.red()
                        )
                        await message.channel.send(embed=em)
                        em = discord.Embed(
                            title="ěëŠ ę°ě§ đ¨",
                            description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\në§íŹ - {}\nę˛˝ęł  - {}".format(message.author.mention,message.content,
                                                                                      self.count.count(message.author.id)),
                            colour=discord.Color.red()
                        )
                        await self.bot.get_channel(892742664506732574).send(embed=em)
                    else:

                        em = discord.Embed(
                            title="ěëŠ ę°ě§ đ¨",
                            description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\nę˛˝ęł  - {}".format(message.author.mention,
                                                                                      self.count.count(message.author.id)),
                            colour=discord.Color.red()
                        )
                        await message.channel.send(embed=em)
                        em = discord.Embed(
                            title="ěëŠ ę°ě§ đ¨",
                            description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\në§íŹ - {}\nę˛˝ęł  - {}".format(message.author.mention,
                                                                                               message.content,
                                                                                               self.count.count(
                                                                                                   message.author.id)),
                            colour=discord.Color.red()
                        )
                        await self.bot.get_channel(892742664506732574).send(embed=em)
                        target = message.author
                        reason = "ěëŠ íěëĄ ě¸í ę˛˝ęł "
                        cur = await self.bot.db_con.execute("SELECT * FROM warn_list WHERE user_id = ?", (target.id,))
                        datas = await cur.fetchall()
                        print(datas)
                        if datas == []:
                            end = datetime.datetime.utcnow() + datetime.timedelta(days=3)
                            end = end.strftime("%Y-%m-%d %H:%M")
                            now = datetime.datetime.utcnow()
                            now = now.strftime("%Y-%m-%d %H:%M:%S")
                            timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[
                                        :-2]
                            punish = "đ 3ěź ëŽ¤í¸"
                            await self.bot.db_con.execute(
                                "INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                (target.id, reason, end, timestamp))
                        elif len(datas) == 1:
                            end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                            end = end.strftime("%Y-%m-%d %H:%M")
                            now = datetime.datetime.utcnow()
                            now = now.strftime("%Y-%m-%d %H:%M:%S")
                            timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[
                                        :-2]
                            punish = "đ 7ěź ëŽ¤í¸"
                            await self.bot.db_con.execute(
                                "INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                (target.id, reason, end, timestamp))
                        else:
                            end = "2100-12-31 23:59"
                            now = datetime.datetime.utcnow()
                            now = now.strftime("%Y-%m-%d %H:%M:%S")
                            timestamp = str(time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[
                                        :-2]
                            punish = "đ ěęľŹ ëŽ¤í¸"
                            await self.bot.db_con.execute(
                                "INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
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
                            title="ę˛˝ęł ę° ëśěŹë¨",
                            description="đŽââď¸ ëśěŹě - {admin}\nđ ëśěŹëě - {user}\n\nâ ěŹě  - `{reason}`\n\n ě˛ë˛ë´ěŠ - {punish}".format(
                                admin=self.bot.user.mention, user=target.mention, reason=reason, punish=punish),
                            timestamp=datetime.datetime.now(),
                            color=discord.Color.red()
                        )
                        wem = discord.Embed(
                            title="ę˛˝ęł ę° ëśěŹëěěľëë¤!",
                            description="đŽââď¸ ëśěŹě - {admin}\nđ ëśěŹëě - {user}\n\nâ ěŹě  - `{reason}`\n\n ě˛ë˛ë´ěŠ - {punish}".format(
                                admin=self.bot.user.mention, user=target.mention, reason="ěëŠ íěëĄ ě¸í ę˛˝ęł ",
                                punish=punish),
                            timestamp=datetime.datetime.now(),
                            color=discord.Color.red()
                        )
                        await message.channel.send(
                            content=f"{message.author.mention}, ěëŠíěëĽź ëŠěśě´ěŁźě¸ě! \něëŠíěëĄ ě¸í´ ę˛˝ęł ę° ëśěŹëěěľëë¤! ěŁźěíě¸ě.", embed=wem)
                        await self.bot.get_channel(884219305942740992).send(embed=em)
                        while message.author.id in self.count:
                            self.count.remove(message.author.id)
                else:
                    if message.channel.topic.find("igivt") == -1:
                        await message.delete()
                        self.count.append(message.author.id)
                        if self.count.count(message.author.id) <= 2:
                            em = discord.Embed(
                                title="ěëŠ ę°ě§ đ¨",
                                description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\nę˛˝ęł  - {}".format(message.author.mention,
                                                                                          self.count.count(
                                                                                              message.author.id)),
                                colour=discord.Color.red()
                            )
                            await message.channel.send(embed=em)
                            em = discord.Embed(
                                title="ěëŠ ę°ě§ đ¨",
                                description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\në§íŹ - {}\nę˛˝ęł  - {}".format(
                                    message.author.mention, message.content,
                                    self.count.count(message.author.id)),
                                colour=discord.Color.red()
                            )
                            await self.bot.get_channel(892742664506732574).send(embed=em)
                        else:
                            em = discord.Embed(
                                title="ěëŠ ę°ě§ đ¨",
                                description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\nę˛˝ęł  - {}".format(message.author.mention,
                                                                                          self.count.count(
                                                                                              message.author.id)),
                                colour=discord.Color.red()
                            )
                            await message.channel.send(embed=em)
                            em = discord.Embed(
                                title="ěëŠ ę°ě§ đ¨",
                                description="{}ëě´ ěëŠëĽź ěëíë ¤ë íěëĽź ę°ě§íěěľëë¤.\në§íŹ - {}\nę˛˝ęł  - {}".format(
                                    message.author.mention,
                                    message.content,
                                    self.count.count(
                                        message.author.id)),
                                colour=discord.Color.red()
                            )
                            await self.bot.get_channel(892742664506732574).send(embed=em)
                            target = message.author
                            reason = "ěëŠ íěëĄ ě¸í ę˛˝ęł "
                            cur = await self.bot.db_con.execute("SELECT * FROM warn_list WHERE user_id = ?",
                                                                (target.id,))
                            datas = await cur.fetchall()
                            print(datas)
                            if datas == []:
                                end = datetime.datetime.utcnow() + datetime.timedelta(days=3)
                                end = end.strftime("%Y-%m-%d %H:%M")
                                now = datetime.datetime.utcnow()
                                now = now.strftime("%Y-%m-%d %H:%M:%S")
                                timestamp = str(
                                    time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[
                                            :-2]
                                punish = "đ 3ěź ëŽ¤í¸"
                                await self.bot.db_con.execute(
                                    "INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                    (target.id, reason, end, timestamp))
                            elif len(datas) == 1:
                                end = datetime.datetime.utcnow() + datetime.timedelta(days=7)
                                end = end.strftime("%Y-%m-%d %H:%M")
                                now = datetime.datetime.utcnow()
                                now = now.strftime("%Y-%m-%d %H:%M:%S")
                                timestamp = str(
                                    time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[
                                            :-2]
                                punish = "đ 7ěź ëŽ¤í¸"
                                await self.bot.db_con.execute(
                                    "INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
                                    (target.id, reason, end, timestamp))
                            else:
                                end = "2100-12-31 23:59"
                                now = datetime.datetime.utcnow()
                                now = now.strftime("%Y-%m-%d %H:%M:%S")
                                timestamp = str(
                                    time.mktime(datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S').timetuple()))[
                                            :-2]
                                punish = "đ ěęľŹ ëŽ¤í¸"
                                await self.bot.db_con.execute(
                                    "INSERT INTO mute_list(user_id,reason,end_dates,stamp) VALUES (?,?,?,?)",
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
                                title="ę˛˝ęł ę° ëśěŹë¨",
                                description="đŽââď¸ ëśěŹě - {admin}\nđ ëśěŹëě - {user}\n\nâ ěŹě  - `{reason}`\n\n ě˛ë˛ë´ěŠ - {punish}".format(
                                    admin=self.bot.user.mention, user=target.mention, reason=reason, punish=punish),
                                timestamp=datetime.datetime.now(),
                                color=discord.Color.red()
                            )
                            wem = discord.Embed(
                                title="ę˛˝ęł ę° ëśěŹëěěľëë¤!",
                                description="đŽââď¸ ëśěŹě - {admin}\nđ ëśěŹëě - {user}\n\nâ ěŹě  - `{reason}`\n\n ě˛ë˛ë´ěŠ - {punish}".format(
                                    admin=self.bot.user.mention, user=target.mention, reason="ěëŠ íěëĄ ě¸í ę˛˝ęł ",
                                    punish=punish),
                                timestamp=datetime.datetime.now(),
                                color=discord.Color.red()
                            )
                            await message.channel.send(
                                content=f"{message.author.mention}, ěëŠíěëĽź ëŠěśě´ěŁźě¸ě! \něëŠíěëĄ ě¸í´ ę˛˝ęł ę° ëśěŹëěěľëë¤! ěŁźěíě¸ě.",
                                embed=wem)
                            await self.bot.get_channel(884219305942740992).send(embed=em)
                            while message.author.id in self.count:
                                self.count.remove(message.author.id)




def setup(bot):
    bot.add_cog(modmail(bot))