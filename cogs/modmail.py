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
class modmail(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dict = {
            "892557938554699777":"📧 일반 문의",
            "892558109770412042":"👮‍♂️ 신고 문의",
            "892558436800290817":"🙌 팀 지원 문의"
        }


    @Cog.listener()
    async def on_message(self,message:discord.Message):
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