import discord
from datetime import datetime
from utils import config


async def on_clip(reaction, user, bot):

    # Check for Needed Reacts
    if reaction.count < 5:
        return

    # The message
    msg = reaction.message

    # Check for Message Already In
    if config.on_clipboard(msg.id):
        config.increase_clip(msg.id)
        return

    # Set the Clipboard Channel
    clipboard = bot.get_channel(config.CHANNEL_ID_CLIPBOARD)

    # have to add a check here to make sure its not the pin board itself
    if msg.channel == clipboard:
        return

    # Check if Message Author is in "No Clip" List
    if msg.author in config.get_noclip_members():
        return

    # Setup Embed
    embed = discord.Embed(colour=discord.Colour(0xca0003), description=msg.content, timestamp=datetime.now())

    if msg.embeds:
        data = msg.embeds[0]
        if data.type == 'image':
            embed.set_image(url=data.url)

    if msg.attachments:
        file = msg.attachments[0]
        if file['url'].lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
            embed.set_image(url=file['url'])
        else:
            embed.add_field(name='Attachment', value='[' + file['url'] + '](' + file['filename'] + ')', inline=False)

    embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url)

    clip_msg = await bot.send_message(clipboard, content="ðŸ“‹ from {0.mention}".format(msg.channel), embed=embed)

    config.add_clipboard(msg.id, clip_msg.id)


async def remove_clip(reaction, bot):

    # The message
    msg = reaction.message

    # Check for Message Already In
    if config.on_clipboard(msg.id):
        config.decrease_clip(msg.id)
        return
