import discord
from discord.ext import commands
import logging
import asyncio
from utils import config
from utils.emojis import *
from clipboard import on_clip
from bookmark import on_bookmark
from pins import on_pin


# BOT LOGGING
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='marxbot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Bot Description
description = '''Famed Economic Theorist and Supporter of the Working Peoples' Servers.'''

# This specifies what extensions to load when the bot starts up
startup_extensions = ["general", "roles", "music", "wiki", "staff", "tweet_watch"]

# Setup Bot
bot = commands.Bot(command_prefix='!', description="Karl Marxbot.")


@bot.event
async def on_ready():
    print('..... Marxbot has started .....')
    await bot.change_presence(game=discord.Game(name='Communism Simulator BETA'))


# Welcome Message
@bot.event
async def on_member_join(member):
    # Define Channels
    channel_lobby = bot.get_channel(config.CHANNEL_ID_LOBBY)
    channel_info = bot.get_channel(config.CHANNEL_ID_INFO)
    channel_updates = bot.get_channel(config.CHANNEL_ID_UPDATES)

    # Get Probie Role
    probie_role = discord.utils.get(member.server.roles, id=config.ROLE_ID_DEFAULT)
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

    # Send Private Welcome Message
    await bot.send_message(member, wmsg)


# Check Messages
@bot.event
async def on_message(message):

    # Check for Counting Message & Prevent Bot from Checking Own Messages for Endless Loop
    if message.channel.id == config.CHANNEL_ID_COUNTING and message.author != bot.user:

        new_number = message.content

        # Is the message strictly a number?
        if new_number.isdigit():
            # Is it the next number?
            if int(new_number) == (config.CURRENT_COUNT + 1):
                # Increase the Count
                config.CURRENT_COUNT = (new_number + 1)
            else:
                config.CURRENT_COUNT = 0
                await bot.send_message(message.channel, "**ALERT**: Sorry, that number is not correct! Start over at 1.")
        else:
            config.CURRENT_COUNT = 0
            await bot.send_message(message.channel, "**ALERT**: Sorry, numbers only! Start over at 1.")

    # Process the rest of the Commands
    await bot.process_commands(message)


# Handle Reacts (Pin, Clip, Bookmark
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == bookmark_emoji:
        await on_bookmark(reaction, user, bot)
    elif reaction.emoji == paperclip_emoji:
        await on_clip(reaction, user, bot)
    elif reaction.emoji == pushpin_emoji:
        await on_pin(reaction, bot)


# Remove Reaction
# @bot.event
# async def on_reaction_remove(reaction, user):
#    # delete message in #pin_board on removal of pushpin emoji
#    if reaction.emoji == paperclip_emoji:
#        await remove_clip(reaction.message, bot)


async def save_count():
    await bot.wait_until_ready()
    while not bot.is_closed:

        updated = config.update_counting()

        if updated:
            print("Counting stats have been updated.")
        else:
            print("ERROR: Counting stats could not be updated.")

        await asyncio.sleep(600)  # task runs every 600 seconds


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
            if extension == 'tweet_watch':
                raise e

    bot.loop.create_task(save_count())
    bot.run(config.BOT_TOKEN)
