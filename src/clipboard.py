# From MitchWeaver DisKvlt-Bot
from datetime import datetime
import requests
from utils import config


async def on_clip(reaction, user, bot):

    # Check for Needed Reacts
    if reaction.count < 5:
        return

    # Check for any message.
    if reaction.message.clean_content is None:
        return

    # Set the Clipboard Channel
    clipboard = bot.get_channel(config.CHANNEL_ID_CLIPBOARD)

    # have to add a check here to make sure its not the pin board itself
    if reaction.message.channel == clipboard:
        return

    NAME = "Unknown User"
    if user.nick is not None:
        NAME = user.nick
    elif user.name is not None:
        NAME = user.name

    # ----------- Prevent multiple posts -----------------
    if reaction.message.embeds is None or len(reaction.message.embeds) == 0:
        async for _message in bot.logs_from(clipboard, limit=40):
            if len(reaction.message.clean_content) > 1:
                if reaction.message.author.name.lower() in _message.clean_content.lower():
                    if reaction.message.clean_content.lower() in _message.clean_content.lower():
                        return
    # ----------------------------------------------------

    # date stamp
    date = datetime.now().strftime('%a %d %b %y')

    try:
        # if has attachments, it is an uploaded picture
        try:
            json = str(reaction.message.attachments[0]).split("'")
        except:
            try:
                json = str(reaction.message.attachments[1]).split("'")
            except:
                json = str(reaction.message.attachments[2]).split("'")

        file = open('/tmp/image2.png', 'wb')
        try:
            image = requests.get(json[5]).content
        except:
            try:
                image = requests.get(json[4]).content
            except:
                try:
                    image = requests.get(json[3]).content
                except:
                    pass

        file.write(image)
        file.close()

        text = "From " + reaction.message.author.mention \
                + "  ~  " + date + reaction.message.clean_content
        if len(reaction.message.clean_content) > 2:
            text = "From " + reaction.message.author.mention \
                + "  ~  " + date + "\n" + '```' + \
                reaction.message.clean_content + '```'

        await bot.send_file(clipboard, "/tmp/image2.png", content=text)
    except:
        # if the above failed, its only text -- no file
        try:
            if "http" not in reaction.message.clean_content.lower() \
                    and "www" not in reaction.message.clean_content.lower():
                text = "From " + reaction.message.author.mention + "  ~  " \
                        + date + "\n" + \
                        '```' + reaction.message.clean_content + '```'
            else:
                text = "From " + reaction.message.author.mention  + "  ~  " \
                        + date + "\n" \
                        + reaction.message.clean_content

            await bot.send_message(clipboard, text)
        except:
            pass


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
