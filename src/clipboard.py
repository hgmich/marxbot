import discord
from datetime import datetime
from utils import config


async def on_clip(reaction, user, bot):

    # Check for Needed Reacts
    if reaction.count < 5:
        return

    # The message
    msg = reaction.message

    await clip_message(msg, bot)


async def remove_clip(reaction, bot):

    # The message
    msg = reaction.message

    # Check for Message Already In
    if config.on_clipboard(msg.id):
        config.decrease_clip(msg.id)
        return


async def clip_message(message, bot):

    # Check for Message Already On Clipboard
    if config.on_clipboard(message.id):
        config.increase_clip(message.id)
        return

    # Set the Clipboard Channel
    clipboard = bot.get_channel(config.CHANNEL_ID_CLIPBOARD)

    # have to add a check here to make sure its not the pin board itself
    if message.channel == clipboard:
        return

    # Check if Message Author is in "No Clip" List
    if message.author in config.get_noclip_members():
        return

    # Get URL to Post
    server_id = message.server.id
    channel_id = message.channel.id
    message_id = message.id
    embed_url = "https://discordapp.com/channels/" + server_id + "/" + channel_id + "/" + message_id

    # Setup Embed
    embed = discord.Embed(colour=discord.Colour(0xca0003), description="[View Original Post](" + embed_url + ")",
                          timestamp=datetime.now())

    # Add Message Content Field
    embed.add_field(name='Message', value=message.content, inline=False)

    if message.embeds:
        data = message.embeds[0]
        if data.type == 'image':
            embed.set_image(url=data.url)

    if message.attachments:
        file = message.attachments[0]
        if file['url'].lower().endswith(('png', 'jpeg', 'jpg', 'gif', 'webp')):
            embed.set_image(url=file['url'])
        else:
            embed.add_field(name='Attachment', value='[' + file['url'] + '](' + file['filename'] + ')', inline=False)

    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)

    clip_msg = await bot.send_message(clipboard, content="📋 - from {0.mention}".format(message.channel), embed=embed)

    config.add_clipboard(message.id, clip_msg.id)
