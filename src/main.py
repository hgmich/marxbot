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
startup_extensions = ["general", "roles", "games", "events", "music", "wiki", "staff", "tweet_watch"]

# Setup Bot
bot = commands.Bot(command_prefix='!', description="Karl Marxbot.")


@bot.event
async def on_ready():
    print('..... Marxbot has started .....')
    await bot.change_presence(game=discord.Game(name='Bot Version 2.9'))


# Welcome Message
@bot.event
async def on_member_join(member):

    # Define Channels
    channel_join_leave = bot.get_channel(config.CHANNEL_ID_JOINLEAVE)
    channel_lobby = bot.get_channel(config.CHANNEL_ID_LOBBY)
    channel_welcome = bot.get_channel(config.CHANNEL_ID_WELCOME)

    # Get Probationary Role
    probie_role = discord.utils.get(member.server.roles, id=config.ROLE_ID_DEFAULT)
    await bot.add_roles(member, probie_role)

    # Setup Welcome DM
    wmsg = "Hello {0.mention}, and welcome to LeftDisc, a fun, safe, inclusive, queer-friendly social community for " \
           "leftists. Thanks for joining, but first some housekeeping. You'll notice that you can only view the " \
           "{1.mention}, along with {2.mention} (the rules channel). This is because you are considered a **Psyop**, " \
           "a probationary member. To protect member privacy, as well as prevent spam and trolling from unsavory " \
           "characters, all members go through a verification process. \n\n Please ping the staff using `@mods` and " \
           "once contacted, share a bit about your political leanings and some social media links (e.g. Twitter, " \
           "Mastodon, Reddit). **If you fail to provide details to verify yourself within 24 hours, you will be " \
           "kicked from the server**. In the meantime, please read the {2.mention} channel and familiarize yourself " \
           "with our rules. Thanks, and again, welcome to LeftDisc!" \
           "".format(member, channel_lobby, channel_welcome)

    # Send Private Welcome Message
    await bot.send_message(member, wmsg)

    # Setup Alert Message
    alert_msg = "A new user, {0.mention}, has joined the server.".format(member)

    # Post Alert in Join-Leave Channel
    await bot.send_message(channel_join_leave, alert_msg)


# Leave Alert
@bot.event
async def on_member_remove(member):
    # Define Channel
    channel_join_leave = bot.get_channel(config.CHANNEL_ID_JOINLEAVE)

    # Setup Alert Message
    display = member.display_name
    user_num = member.name + "#" + member.discriminator
    user_id = member.id
    alert_msg = "{0.mention} has left the server. **Display**: ".format(member) + display + ", **User**: " + user_num \
                + ", **UserID**: " + user_id

    # Post Alert in Join-Leave Channel
    await bot.send_message(channel_join_leave, alert_msg)

    # Remove from Game Profiles
    config.delete_game_profile(user_id)


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
                config.CURRENT_COUNT = (config.CURRENT_COUNT + 1)
            else:
                config.CURRENT_COUNT = 0
                await bot.send_message(message.channel, "**ALERT**: Sorry, that number is not correct! Start over at 1.")
        else:
            config.CURRENT_COUNT = 0
            await bot.send_message(message.channel, "**ALERT**: Sorry, numbers only, no words, emojis, etc! Start over at 1.")

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
