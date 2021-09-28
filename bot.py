import os
import discord
from discord.ext import commands
from tools.autocogs import AutoCogs
from dotenv import load_dotenv
import aiosqlite
from pycord_components import PycordComponents
import config
load_dotenv(verbose=True)

create_warnlist_table = """ 
CREATE TABLE IF NOT EXISTS warn_list (
    user_id integer,                    
    reason text,
    dates text DEFAULT (strftime('%Y-%m-%d %H:%M:%S',datetime('now','localtime')))
);"""
create_muteist_table = """ 
CREATE TABLE IF NOT EXISTS mute_list (
    user_id integer,                 
    reason text,
    end_dates text,
    dates text DEFAULT (strftime('%Y-%m-%d %H:%M',datetime('now','localtime')))
);"""

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command("help")
        AutoCogs(self)


    async def check_db(self):
        async with aiosqlite.connect("db/db.db") as con:
            await con.execute(create_warnlist_table)
            await con.execute(create_muteist_table)
            await con.commit()

    async def on_ready(self):
        """Called upon the READY event"""
        await self.check_db()
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(name="SpaceDEV",
                                                                                               type=discord.ActivityType.listening))
        print("Bot is ready.")

    async def is_owner(self, user):
        if user.id in config.OWNER:
            return True


    async def create_db_con(self=None):
        MyBot.db_con = await aiosqlite.connect("db/db.db")




INTENTS = discord.Intents.all()
my_bot = MyBot(command_prefix="s.", intents=INTENTS)
PycordComponents(bot=my_bot)

if __name__ == "__main__":
    my_bot.loop.run_until_complete(MyBot.create_db_con())
    my_bot.run(os.getenv('TOKEN'))