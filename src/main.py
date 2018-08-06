import discord
from discord.ext import commands
import logging
import asyncio

# BOT LOGGING

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='marxbot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''Famed Economic Theorist and Supporter of the Working Peoples' Servers.'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ["general", "roles", "music", "wiki", "staff", "tweet_watch"]

bot = commands.Bot(command_prefix='!', description="Karl Marxbot.")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game=discord.Game(name='Communism Simulator'))


# Welcome Message
@bot.event
async def on_member_join(member):
    # Define Channels
    # channel_general = bot.get_channel('338594020101980160')
    channel_lobby = bot.get_channel('359182653934665749')
    channel_info = bot.get_channel('356968473819348994')
    channel_updates = bot.get_channel('356972304019881984')

    # Get Probie Role
    probie_role = discord.utils.get(member.server.roles, name='Psyops')
    await bot.add_roles(member, probie_role)

    wmsg = "Hello {0.mention}, and welcome to LeftDisc, a leftist Discord server. We thank you for " \
           "joining, but first some housekeeping. You'll notice that you can only view the {1.mention}, along with " \
           "{2.mention} (the rules channel) and {3.mention} (the updates and announcements channel). " \
           "This is because you are considered a **Psyop**, a probationary member. To protect member privacy, as well " \
           "as prevent spam and trolling from unsavory characters, all members go through a verification process. " \
           "Please let us know how you heard about LeftDisc, and provide some links to your social media accounts in " \
           "the {1.mention} channel. If you are uncomfortable doing so, please contact a staff member to discuss. " \
           "**If you fail to provide details to verify you within 24 hours, you will be kicked from the server**. " \
           "In the meantime, please read the {2.mention} channel and familiarize yourself with our purpose and rules. " \
           "Check out the {3.mention} channel for updates and announcements. Thanks, and again, welcome to LeftDisc!" \
           "".format(member, channel_lobby, channel_info, channel_updates)

    wpm = "Hello comrade, and welcome to LeftDisc, a server, a home, for leftists. A few things to note: " \
          "Take a look at the {0.mention} channel; it lists what we are about as well as the rules. " \
          "Important news will be posted in {1.mention}. Again, thank you for joining the server, and the " \
          "struggle. Please check {2.mention} for more information.".format(channel_info, channel_updates, channel_lobby)

    # Send Welcome Message to the Probie Lobby
    # await bot.send_message(channel_lobby, wmsg)

    # Send Private Welcome Message
    await bot.send_message(member, wmsg)


# Check Messages
@bot.event
async def on_message(message):

    # Process the rest of the Commands
    await bot.process_commands(message)


# Auto-Pin on Pushpin Reactions in Shitposting Channels
@bot.event
async def on_reaction_add(reaction, user):

    # Define Allowed Channels (Shitposting, Queer Shitposting, Nice Town, Health & Fitness, Queer)
    channels = []
    channels.append(bot.get_channel('386609440863813642'))
    channels.append(bot.get_channel('361260914164498433'))
    channels.append(bot.get_channel('425809470623318026'))
    channels.append(bot.get_channel('449022450806554635'))
    channels.append(bot.get_channel('359468983499489282'))

    # Check if the reaction is pushpin
    if str(reaction.emoji) == '\N{PUSHPIN}' and reaction.count >= 4 and not reaction.message.pinned and reaction.message.channel in channels:
        current_pinned = await bot.pins_from(reaction.message.channel)
        if len(current_pinned) < 50:
            await bot.pin_message(reaction.message)
        else:
            await bot.send_message(reaction.message.channel, "I cannot pin the message. We have reached the maximum "
                                                             "number of pins comrades!")

# Goodbye Message
# @bot.event
# async def on_member_remove(member):
#    channel = bot.get_channel('108369515502411776')
#    fmt = ":wave: Goodbye {0}, we're sad to see you go!".format(member.name)
#    await bot.send_message(channel, fmt)


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
            if extension == 'tweet_watch':
                raise e

    bot.run('tokenhere')
