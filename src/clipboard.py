# From MitchWeaver DisKvlt-Bot
import discord
from datetime import datetime
from utils import config


async def on_clip(reaction, user, bot):

    # Check for Needed Reacts
    if reaction.count < 5:
        return

    # The message
    msg = reaction.message

    # Set the Clipboard Channel
    clipboard = bot.get_channel(config.CHANNEL_ID_CLIPBOARD)

    # have to add a check here to make sure its not the pin board itself
    if msg.channel == clipboard:
        return

    # date stamp
    date = datetime.now().strftime('%a %d %b %y')

    # Setup Embed
    embed = discord.Embed(colour=discord.Colour(0xca0003), description=msg.content, timestamp=date)

    if msg.embeds:
        data = msg.embeds[0]
        if data.type == 'image':
            embed.set_image(url=data.url)

    if msg.attachments:
        file = msg.attachments[0]
        if file.url.lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
            embed.set_image(url=file.url)
        else:
            embed.add_field(name='Attachment', value=f'[{file.filename}]({file.url})', inline=False)

    embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url_as(format='png'))

    clip_msg = await bot.say(content="📋 from {0.mention}".format(msg.channel), embed=embed)

    config.add_clipboard(msg.id, clip_msg.id)


async def remove_clip(reaction, bot):

    # Set the Clipboard Channel
    clipboard = bot.get_channel(config.CHANNEL_ID_CLIPBOARD)

    try:
        for message in bot.messages:
            if message.channel == clipboard:
                if message == reaction.message:
                    try:
                        await bot.delete_message(message)
                    except:
                        pass
                    return
    except:
        pass
