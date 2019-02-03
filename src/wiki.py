import discord
from discord.ext import commands
from utils import checks
import wikipedia
import random


class Wiki:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # WIKIPEDIA BOT COMMANDS *********************** #
    # ********************************************** #

    # COMMAND: !wiki
    @commands.group(pass_context=True)
    @checks.is_member()
    async def wiki(self, ctx):
        """Search Wikipedia (EN) for articles and information."""

        if ctx.invoked_subcommand is None:
            await self.bot.say('**ERROR**: Invalid command passed. Please use `!wiki search` or `!wiki suggest`.')

    # COMMAND: !wiki search
    @wiki.command(name='search')
    @checks.is_member()
    async def wiki_search(self, *, query: str):
        """Searches Wikipedia for an article based on the given search phrase."""

        # Start the Embed Return message
        embed = discord.Embed(title="Wikipedia Search Result", colour=7829367,
                              description="Search result for: '" + query + "'")

        # Search the Wikipedia
        try:
            results = wikipedia.search(query)

            if len(results) == 0:

                # Add Page Does Not Exist Message
                page_text = "'" + query + "' does not match any pages. Try another query."

                embed.add_field(name="Page Error", value=page_text, inline=False)
                embed.set_footer(text="Error")

            elif (len(results) == 1) or (query in results):

                # Get Page and Summary
                page = wikipedia.page(query)
                summary = wikipedia.summary(query, sentences=3)

                # Set Author for Link
                embed.set_author(name="Wikipedia", url=page.url)

                # Get Images:
                embed.set_thumbnail(url=random.choice(page.images))

                # Set footer, link to page:
                embed.set_footer(text=page.url)

                # Set URL
                embed.url = page.url

                # Set Summary
                embed.add_field(name="Summary", value=summary, inline=False)

            else:

                embed.add_field(name="Multiple Results", value="Multiple results were found. Please narrow your search "
                                                               "or search one of the following *exactly* as it appears "
                                                               "below or use the `suggest` command.", inline=False)
                r_text = ""
                i = 1

                for r in results:
                    r_text += "**" + str(i) + "**. " + r + "\n"
                    i += 1

                embed.add_field(name="Suggestions", value=r_text, inline=False)

        except wikipedia.exceptions.DisambiguationError as e:

            # Add Disambiguation fields.
            disam_text = "Your query was not specific enough. '" + query + "' may refer to:"
            disam_list = ""

            opts = 1

            for opt in e.options:
                disam_list += "**" + str(opts) + ".** " + opt + "\n"
                opts += 1

                if opts > 10:
                    break

            embed.add_field(name="Disambiguation Error", value=disam_text, inline=False)
            embed.add_field(name="Suggestions", value=disam_list, inline=False)
            embed.set_footer(text="Error")

        except wikipedia.exceptions.PageError:

            # Add Page Does Not Exist Message
            page_text = "'" + query + "' does not match any pages. Try another query."

            embed.add_field(name="Page Error", value=page_text, inline=False)
            embed.set_footer(text="Error")

        except Exception as e:
            self.bot.say("**Error**: " + str(e))
            return

        # Send the Embed
        await self.bot.say(embed=embed)

    # COMMAND: !wiki suggest
    @wiki.command(name='suggest')
    @checks.is_member()
    async def wiki_suggest(self, *, query: str):
        """Searches Wikipedia for an article based on the given search phrase and returns the best suggestion."""

        # Start the Embed Return message
        embed = discord.Embed(title="Wikipedia Search Result", colour=7829367,
                              description="Search result for: '" + query + "'")

        # Search the Wikipedia
        try:
            suggestion = wikipedia.suggest(query)

            if suggestion is None:

                # Add Page Does Not Exist Message
                page_text = "'" + query + "' does not match any pages. Try another query."

                embed.add_field(name="Page Error", value=page_text, inline=False)
                embed.set_footer(text="Error")

            else:

                # Get Page and Summary
                page = wikipedia.page(suggestion)
                summary = wikipedia.summary(suggestion, sentences=3)

                # Set Author for Link
                embed.set_author(name="Wikipedia", url=page.url)

                # Get Images:
                embed.set_thumbnail(url=random.choice(page.images))

                # Set footer, link to page:
                embed.set_footer(text=page.url)

                # Set URL
                embed.url = page.url

                # Set Summary
                embed.add_field(name="Summary", value=summary, inline=False)

        except wikipedia.exceptions.DisambiguationError as e:

            # Add Disambiguation fields.
            disam_text = "Your query was not specific enough. '" + query + "' may refer to:"
            disam_list = ""

            opts = 1

            for opt in e.options:
                disam_list += "**" + str(opts) + ".** " + opt + "\n"
                opts += 1

                if opts > 10:
                    break

            embed.add_field(name="Disambiguation Error", value=disam_text, inline=False)
            embed.add_field(name="Suggestions", value=disam_list, inline=False)
            embed.set_footer(text="Error")

        except wikipedia.exceptions.PageError:

            # Add Page Does Not Exist Message
            page_text = "'" + query + "' does not match any pages. Try another query."

            embed.add_field(name="Page Error", value=page_text, inline=False)
            embed.set_footer(text="Error")

        except Exception as e:
            self.bot.say("**Error**: " + str(e))
            return

        # Send the Embed
        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Wiki(bot))
