# From MitchWeaver DisKvlt-Bot
from datetime import datetime
import requests


async def on_bookmark(reaction, user, bot):
    print("Reaction was bookmark!")

    # date stamp
    date = datetime.now().strftime('%a %d %b %y')

    # if has attachments, it is an uploaded picture
    try:
        json = str(reaction.message.attachments[0]).split("'")

        file = open('/tmp/image2.png', 'wb')
        file.write(requests.get(json[5]).content)
        file.close()

        # if the user also posted text with this message, post it
        # for some reason discord uploads have some weird 1 character long
        # text. Not sure what it is, it's not a \n or " "
        text = "From " + reaction.message.author.mention \
               + "  ~  " + date + reaction.message.clean_content
        if len(reaction.message.clean_content) > 1:
            text = "From " + reaction.message.author.mention + "  ~  " \
                   + date + "\n" \
                   + '```' + reaction.message.clean_content + '```'

        try:
            await bot.send_file(user, "/tmp/image2.png", content=text)
        except:
            pass

    except:
        try:
            if "http" not in reaction.message.clean_content.lower() \
                    and "www" not in reaction.message.clean_content.lower():
                text = "From " + reaction.message.author.mention + "  ~  " \
                       + date + "\n" + \
                       '```' + reaction.message.clean_content + '```'
            else:
                text = "From " + reaction.message.author.mention + "  ~  " \
                       + date + "\n" \
                       + reaction.message.clean_content

            await bot.send_message(user, text)

        except:
            pass
