import discord
from discord.ext import commands
import platform

from cogs._db_helper import Database


class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Helper functions
    async def create_timer(self, author, timer_name, interval_time, interval_miss_limit, recipient_list, message, status=0):
        recipient_list = ",".join([str(r.id) for r in recipient_list])

        self.bot.timers[author][timer_name] = {'interval_time': interval_time, 'interval_miss': interval_miss_limit,
                                               'recipient_list': recipient_list, 'message': message, 'status': status}

        insert_successful = await self.bot.db.insert(author, timer_name, interval_time, interval_miss_limit, recipient_list, message, status)

        return insert_successful

    async def log_error(self, error):
        await self.bot.errors_channel.send(error)

    @commands.command()
    async def ping(self, ctx):
        """
        Check the latency of bot reply
        Usage: !ping
        """
        await ctx.send(f"Latency = {round(self.bot.latency * 1000)}ms")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx):
        """
        Clears all the messages from active channel
        (only available to server owners)
        Usage: !clear
        """
        await ctx.channel.purge(limit=10000)

    @commands.command(aliases=['stat', 'info', 'bot'])
    async def stats(self, ctx):
        """
        Displays Bot Statistics.
        """
        python_version = platform.python_version()
        discord_version = discord.__version__
        server_count = str(len(self.bot.guilds))
        member_count = str(len(set(self.bot.get_all_members())))

        embed = discord.Embed(title=f'{self.bot.user.name} Stats', description='\uFEFF', colour=ctx.author.colour, timestamp=ctx.message.created_at)

        embed.add_field(name='Bot Version:', value=self.bot.version)
        embed.add_field(name='Python Version:', value=python_version)
        embed.add_field(name='Discord.Py Version', value=discord_version)
        embed.add_field(name='Total Guilds:', value=server_count)
        embed.add_field(name='Total Users:', value=member_count)
        embed.add_field(name='Bot Developer:', value="Prem Nagdeo")

        embed.set_footer(text=f"{self.bot.user.name}")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def create(self, ctx, *, timer_name):
        """
        Creates and sets up a new timer to be used
        Usage: !create <timer_name>
        """

        def messagecheck(m):
            return m.author == ctx.author and m.content is not None and m.channel == ctx.channel

        await ctx.message.channel.send(f"{ctx.message.author.mention} Enter the time interval in which you want to be pinged in HH:MM format")
        interval_time = await self.bot.wait_for('message', check=messagecheck)

        # Interval time input validation
        is_interval_time_valid = True
        try:
            h, m = (int(i) for i in interval_time.content.split(":"))
            if h == 0 and m == 0:
                is_interval_time_valid = False
        except:
            is_interval_time_valid = False

        while not is_interval_time_valid:
            await ctx.message.channel.send(
                f"{ctx.message.author.mention} Invalid interval time \nPlease enter the interval time in which you want to be pinged in HH:MM format")
            interval_time = await self.bot.wait_for('message', check=messagecheck)

            is_interval_time_valid = True
            try:
                h, m = (int(i) for i in interval_time.content.split(":"))
                if h == 0 and m == 0:
                    is_interval_time_valid = False
            except:
                is_interval_time_valid = False

        interval_time = interval_time.content

        await ctx.message.channel.send(
            f"{ctx.message.author.mention} Enter the maximum number of pings that can be missed by you. (Enter a number) [Default = 1]")
        interval_miss_limit = await self.bot.wait_for('message', check=messagecheck)

        # Interval miss limit validation
        is_interval_miss_limit_valid = True
        try:
            m = int(interval_miss_limit.content.strip())
            if m == 0:
                is_interval_miss_limit_valid = False
        except:
            is_interval_miss_limit_valid = False

        if not is_interval_miss_limit_valid:
            await ctx.message.channel.send(f"{ctx.message.author.mention} Invalid number, Interval Miss limit set to 1")
            interval_miss_limit = 1
        else:
            interval_miss_limit = int(interval_miss_limit.content)

        await ctx.message.channel.send(f"{ctx.message.author.mention} Mention the members you would like to alert (using @)")
        recipients = await self.bot.wait_for('message', check=messagecheck)

        if "@everyone" in recipients.content:
            await ctx.message.channel.send(
                f"{ctx.message.author.mention} Please do not mention everyone. Try again \nMention the members you would like to alert (using @)")
            recipients = await self.bot.wait_for('message', check=messagecheck)

        await ctx.message.channel.send(f"{ctx.message.author.mention} What message would you like to send?")
        message = await self.bot.wait_for('message', check=messagecheck)

        message = message.content
        # Pre processing
        recipient_list = []
        for recipient in recipients.mentions:
            recipient_list.append(recipient)

        await ctx.message.channel.send(f"{ctx.message.author.mention} Timer details:")
        await ctx.message.channel.send(
            "```Timer owner: {author} \nName: {name} \nInterval Time: {intervals}\nInterval Miss Limit: {miss_limit} \nRecipients: {recipients} \nMessage: {message}```"
                .format(author=ctx.message.author, name=timer_name, intervals=interval_time,
                        miss_limit=interval_miss_limit,
                        recipients=', '.join([r.name for r in recipient_list]), message=message))

        confirm_wait = True
        while confirm_wait:
            await ctx.message.channel.send(f"{ctx.message.author.mention} Create timer? (y/n)")
            confirm = await self.bot.wait_for("message", timeout=45)
            if "y" == confirm.content.lower():
                confirm_wait = False
                create_successful = await self.create_timer(ctx.message.author.id, timer_name, interval_time, interval_miss_limit,
                                                            recipient_list, message)
                if create_successful == 'SUCCESS':
                    await ctx.message.channel.send(f"{ctx.message.author.mention} :thumbsup: Timer '{timer_name}' Created!")
                else:
                    if create_successful == "UNIQUE-FAIL":
                        await ctx.message.channel.send(
                            f"{ctx.message.author.mention} This timer already exists. Creation failed\n Use !my-timers to view your timers")
                    else:
                        await ctx.message.channel.send(f"{ctx.message.author.mention} Creation failed. Database error. Error logged")
                        await self.log_error(f'INSERT ERROR creating new timer by {ctx.author.mention} in **{ctx.message.channel}** channel')

            elif "n" == confirm.content.lower():
                confirm_wait = False
                await ctx.message.channel.send(f"{ctx.message.author.mention} :thumbsdown: Timer '{timer_name}' Discarded")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.message.author.mention} You forgot to enter the timer name. Refer to !help create for more information")

    @commands.command()
    async def start(self, ctx, *, timer_name):
        """
        Starts a timer
        Usage: !start <timer_name>
        """

        await ctx.message.channel.send(f"{ctx.message.author.mention} :thumbsup: Timer {timer_name} Started!")

    @start.error
    async def start_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.message.author.mention} You forgot to enter the timer name. Refer to !help start for more information")


def setup(bot):
    bot.add_cog(Commands(bot))
