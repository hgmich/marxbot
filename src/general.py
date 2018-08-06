import discord
from discord.ext import commands
import random
import datetime


class General:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # UN-GROUPED BOT COMMANDS ********************** #
    # ********************************************** #

    # COMMAND: !hello
    @commands.command(pass_context=True)
    async def hello(self, ctx):
        """Say hello to Karl Marxbot. He is very friendly."""
        # we do not want the bot to reply to itself
        if ctx.message.author == self.bot.user:
            return
        else:
            msg = "Hello comrade {0.message.author.mention}, I am Karl Marxbot.".format(ctx)
            await self.bot.send_message(ctx.message.channel, msg)
        
    # COMMAND: !markdown
    @commands.command()
    async def markdown(self):
        """Get the lowdown about Discord markdown."""
        
        msg = "Read up about Discord's markdown here comrade: " \
              "https://support.discordapp.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-"
        
        await self.bot.say(msg)

    # COMMAND: !8ball
    @commands.command(name='8ball', pass_context=True)
    async def eightball(self, ctx, *, question: str):
        """Rolls a magic 8-ball to answer any question you have."""

        if not set(question):
            await self.bot.say("Comrade {0.message.author.mention}, your forgot to ask a question.".format(ctx))
            return

        # Answers List (Classic 8-Ball, 20 Answers)
        answers = ['I am certain of it.',
                   'I have no doubt.',
                   'Yes, definitely.',
                   'It is reliably certain.',
                   'As I see it, yes.',
                   'More likely than not.',
                   'My proletariat sources say yes.',
                   'I have a headache. Bother me again later.',
                   'You are not ready for the answer.',
                   'It is impossible to predict now.',
                   'I would not count on it.',
                   'My reply is no.',
                   'My proletariat sources say no.',
                   'The outlook is not good.',
                   'I find it very doubtful.']

        # SETUP EMBED
        user = ctx.message.author

        if "you a cop" in question.lower():
            answer = "I am not a cop."
        else:
            answer = random.choice(answers)

        embed = discord.Embed(title="Marx's 8-Ball", colour=9043968,
                              description="{0.mention} asked a question of my magic 8-ball.".format(user))
        embed.add_field(name="❓ **Question**", value="*" + question + "*", inline=False)
        embed.add_field(name="🎱 **Answer**", value=answer, inline=False)

        # SEND THE ANSWER EMBED
        await self.bot.say(embed=embed)
        # await self.bot.say('{0.message.author.mention}, '.format(ctx) + random.choice(answers))

    # COMMAND: !roll
    @commands.command()
    async def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format must be NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await self.bot.say(result)

    # COMMAND: !serverinfo
    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        """Displays Information about the Server."""

        # Regions Dictionary
        region_dictionary = {"us-west": "US West",
                             "us-east": "US East",
                             "us-central": "US Central",
                             "eu-west": "EU West",
                             "eu-central": "EU Central",
                             "singapore": "Singapore",
                             "london": "London",
                             "syndey": "Sydney",
                             "amsterdam": "Amsterdam",
                             "frankfurt": "Frankfurt",
                             "brazil": "Brazil"}

        # Online Status
        online_statuses = ["online", "idle", "dnd", "do_not_disturb"]

        # GET EMBED INFO
        server = ctx.message.server
        server_name = server.name
        server_region = region_dictionary[str(server.region)]
        server_date = server.created_at.strftime('%B %d, %Y')
        server_icon = server.icon_url
        server_total_members = server.member_count
        server_id = server.id
        server_owner = server.owner
        server_online_members = sum(1 for member in server.members if str(member.status) in online_statuses)
        server_text_channels = sum(1 for channel in server.channels if str(channel.type) == "text")
        server_voice_channels = sum(1 for channel in server.channels if str(channel.type) == "voice")
        server_roles = sorted(server.roles, key=lambda role: role.position, reverse=True)
        server_roles_list = ", ".join(role.name for role in server_roles if role.hoist is True)

        # Create Embed Table
        embed = discord.Embed(title=server_name, colour=12326244,
                              description="Created on " + server_date)
        embed.set_thumbnail(url=server_icon)
        embed.set_footer(text="Server ID: " + server_id)
        embed.add_field(name="Owner", value="{0.mention}".format(server_owner), inline=True)
        embed.add_field(name="Location", value=server_region, inline=True)
        embed.add_field(name="Online Members", value=server_online_members, inline=True)
        embed.add_field(name="Total Members", value=server_total_members, inline=True)
        embed.add_field(name="Text Channels", value=server_text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=server_voice_channels, inline=True)
        embed.add_field(name="Roles", value=server_roles_list, inline=False)

        await self.bot.say(embed=embed)

    # COMMAND: !invite
    @commands.command(pass_context=True)
    @commands.has_role("Comrades")
    async def invite(self, ctx, duration: int = 1800, maxusers: int = 0):
        """Provides an invite link to the LEFTDISC. Duration is in seconds.
        Max users is the number of times a link can be used."""

        # Check for no duration, default to 0
        if (not duration) or (duration == 0):
            duration = 1800

        if not maxusers:
            maxusers = 0

        # This Server
        server = ctx.message.server

        # Create the Invite
        new_invite = await self.bot.create_invite(server, max_age=duration, max_users=maxusers, unique=False)

        # Send Message with Invite Link
        await self.bot.say('Your newly generated invite link is: {0.url}'.format(new_invite))


def setup(bot):
    bot.add_cog(General(bot))
