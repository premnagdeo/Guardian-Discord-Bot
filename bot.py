import os
from config import TOKEN
import discord
from discord.ext import commands
from collections import defaultdict
from cogs._db_helper import Database
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


description = '''A bot to help you stay safe by creating timers that ping you to check whether you are safe or not. Your personal Guardian.'''
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!', description=description, intents=intents, case_insensitive=True)

bot.db = Database('bot.db')
bot.version = "v0.1"

if __name__ == '__main__':
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(TOKEN)
