import os
from config import TOKEN
import discord
from discord.ext import commands
from collections import defaultdict
from cogs._db_helper import Database

description = '''A bot to help you stay safe by creating timers that ping you to check whether you are safe or not.'''
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!', description=description, intents=intents, case_insensitive=True)
bot.timers = defaultdict(dict)
bot.db = Database('bot.db')
bot.version = "v0.1"

if __name__ == '__main__':
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(TOKEN)
