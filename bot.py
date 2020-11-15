from config import TOKEN
import discord
from discord.ext import commands
import re
import datetime
from collections import defaultdict
import platform

description = '''A bot to help you stay safe by creating timers that ping you to check if you are safe or not.'''
intents = discord.Intents().all()

bot = commands.Bot(command_prefix='!', description=description, intents=intents, case_insensitive=True)

bot.timers = defaultdict(dict)
bot.version = "v0.1"

@bot.event
async def on_ready():
    print("Bot is ready!")
    channel = bot.get_channel(777514113449721886)
    await channel.send('Bot is ready!')


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(777606027742412801)
    await channel.send(f'Hi {member.mention}, welcome to the server! \nAre You There Bot is here to help you stay safe!')

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'{ctx.author.mention} {error}')


@bot.command()
async def ping(ctx):
    """
    Check the latency of bot reply
    Usage: !ping
    """
    await ctx.send(f"Latency = {round(bot.latency * 1000)}ms")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx):
    """
    Clears all the messages from active channel
    (only available to server owners)
    Usage: !clear
    """
    await ctx.channel.purge()

@bot.command(aliases=['stat', 'info', 'bot'])
async def stats(ctx):
    """
    A usefull command that displays bot statistics.
    """
    pythonVersion = platform.python_version()
    dpyVersion = discord.__version__
    serverCount = str(len(bot.guilds))
    memberCount = str(len(set(bot.get_all_members())))

    embed = discord.Embed(title=f'{bot.user.name} Stats', description='\uFEFF', colour=ctx.author.colour, timestamp=ctx.message.created_at)

    embed.add_field(name='Bot Version:', value=bot.version)
    embed.add_field(name='Python Version:', value=pythonVersion)
    embed.add_field(name='Discord.Py Version', value=dpyVersion)
    embed.add_field(name='Total Guilds:', value=serverCount)
    embed.add_field(name='Total Users:', value=memberCount)
    embed.add_field(name='Bot Developer:', value="Prem Nagdeo")

    embed.set_footer(text=f"{bot.user.name}")
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

    await ctx.send(embed=embed)


# Helper function
async def create_timer(author, timer_name, start_time, interval_time, interval_miss_limit, recipient_list, message):
    recipient_list = [r.id for r in recipient_list]
    bot.timers[author][timer_name] = {'start_time': start_time, 'interval_time': interval_time,
                          'interval_miss': interval_miss_limit, 'recipient_list': recipient_list, 'message': message}



@bot.command()
async def create(ctx, *, timer_name="timer1"):
    """
    Creates and sets up a new timer to be used
    Usage: !create <timer_name>
    """

    def timecheck(m):
        if not m.author == ctx.author or not m.content or not m.channel == ctx.channel:
            return False
        h, m = (int(i) for i in m.content.split(":"))
        try:
            datetime.time(h, m)
        except:
            return False
        return True

    def intervalcheck(m):
        if not m.author == ctx.author or not m.content or not m.channel == ctx.channel:
            return False
        h, m = (int(i) for i in m.content.split(":"))
        if h == 0 and m == 0:
            return False

        return True

    def misscheck(m):
        return m.author == ctx.author and m.content is not None and m.channel == ctx.channel

    def membercheck(m):
        return m.author == ctx.author and m.content is not None and m.channel == ctx.channel

    def messagecheck(m):
        return m.author == ctx.author and m.content is not None and m.channel == ctx.channel

    await ctx.message.channel.send(f"{ctx.message.author.mention} Enter the start time in HH:MM format (UTC Time)")
    start_time = await bot.wait_for('message', check=timecheck)

    await ctx.message.channel.send(f"{ctx.message.author.mention} Enter the interval time in which you want to be pinged in HH:MM format")
    interval_time = await bot.wait_for('message', check=intervalcheck)


    await ctx.message.channel.send(f"{ctx.message.author.mention} Enter the maximum number of pings that can be missed by you. (Default = 0)")
    interval_miss_limit = await bot.wait_for('message', check=misscheck)

    await ctx.message.channel.send(f"{ctx.message.author.mention} Mention the members you would like to alert (using @)")
    recipients = await bot.wait_for('message', check=membercheck)

    await ctx.message.channel.send(f"{ctx.message.author.mention} What message would you like to send?")
    message = await bot.wait_for('message', check=messagecheck)

    # Pre processing
    recipient_list = []
    for recipient in recipients.mentions:
        recipient_list.append(recipient)


    await ctx.message.channel.send(f"{ctx.message.author.mention} Timer details:")
    await ctx.message.channel.send(
        "Timer owner: {author} \nName: {name} \nStart Time: {start}\nInterval Time: {intervals}\nInterval Miss Limit: {miss_limit} \nRecipients: {recipients} \nMessage: {message}"
        .format(author=ctx.message.author, name=timer_name, start=start_time.content, intervals=interval_time.content, miss_limit=interval_miss_limit.content,
                recipients=', '.join([r.name for r in recipient_list]), message=message.content))

    confirm_wait = True
    while confirm_wait:
        await ctx.message.channel.send(f"{ctx.message.author.mention} Create timer? (y/n)")
        confirm = await bot.wait_for("message")
        if "y" == confirm.content.lower():
            confirm_wait = False
            await ctx.message.channel.send(f"{ctx.message.author.mention} Timer Created!")
            await create_timer(ctx.message.author.id, timer_name, start_time.content, interval_time.content, interval_miss_limit.content, recipient_list,
                               message.content)
            print(bot.timers)
        elif "n" == confirm.content.lower():
            confirm_wait = False
            await ctx.message.channel.send(f"{ctx.message.author.mention} Timer Discarded")


bot.run(TOKEN)
