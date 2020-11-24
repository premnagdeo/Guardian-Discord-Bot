import discord
from discord.ext import commands

from cogs._db_helper import Database


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.welcome_channel.send(
            f'Hi {member.mention}, Welcome to the server! :wave:\nGuardian Bot is here to help you stay safe!\nGet started with **!help**')

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready!")

        self.bot.welcome_channel = self.bot.get_channel(777606027742412801)
        self.bot.logs_channel = self.bot.get_channel(777672983778033705)
        self.bot.errors_channel = self.bot.get_channel(780930063771369522)

        await self.bot.logs_channel.send('Bot is ready!')

        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching,
                                                                                               name=f"over you. Your Guardian Angel. Use ! to interact with me!"))

        self.bot.db = Database('bot.db')

        if self.bot.db:
            await self.bot.logs_channel.send("Successfully loaded database")
            print("Successfully loaded database")
        else:
            await self.bot.logs_channel.send("Error loading database")
            await self.bot.errors_channel.send("Error loading database")
            print("Error loading database")

        print("RECORDS: ")
        self.bot.db.cursor.execute("SELECT * FROM timers")
        print(self.bot.db.cursor.fetchall())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        await ctx.send(f'{ctx.message.author.mention} Invalid Command')
        await self.bot.errors_channel.send(f'{ctx.author.mention} **{error}** in **{ctx.message.channel}** channel')

        # Handle Value error for numbers


def setup(bot):
    bot.add_cog(Events(bot))
