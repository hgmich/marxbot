import discord
from datetime import datetime


async def on_bookmark(reaction, user, bot):

    # The message
    msg = reaction.message

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

    await bot.send_message(user, content="🔖 – from {0.mention}".format(msg.channel), embed=embed)
