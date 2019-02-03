import discord
from discord.ext import commands
from utils import checks
from utils import config
import datetime
from datetime import datetime


class Staff:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # STAFF-ONLY BOT COMMANDS ********************** #
    # ********************************************** #

    # Load Extension

    @commands.command(pass_context=True)
    @checks.is_admin()
    async def load(self, ctx, extension_name: str):
        """Loads an extension."""

        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as ex:
            await self.bot.say("```py\n{}: {}\n```".format(type(ex).__name__, str(ex)))
            return
        await self.bot.say("{} loaded.".format(extension_name))

    # Unload Extension
    @commands.command(pass_context=True)
    @checks.is_admin()
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""

        self.bot.unload_extension(extension_name)
        await self.bot.say("{} unloaded.".format(extension_name))

    # COMMAND: !setplaying
    @commands.command()
    @checks.is_staff()
    async def setplaying(self, *, game_name: str):
        """Sets Karl's currently playing game."""

        await self.bot.change_presence(game=discord.Game(name=game_name))
        await self.bot.say("I just started playing this game, **{0}**! You should try it!".format(game_name))

    # COMMAND: !comrade
    @commands.command(pass_context=True)
    @checks.is_staff()
    async def comrade(self, ctx, user: discord.Member):
        """Promotes a Psyop to a Comrade granting full server access."""

        # User to make Comrade
        # user = discord.utils.get(ctx.message.server.members, name=username)
        role_probie = discord.utils.get(ctx.message.server.roles, name="Psyops")
        role_comrade = discord.utils.get(ctx.message.server.roles, name="Comrades")

        new_roles = [role_comrade if x == role_probie else x for x in user.roles]

        # Get Channels
        channel_general = self.bot.get_channel(config.CHANNEL_ID_GENERAL)
        channel_info = self.bot.get_channel(config.CHANNEL_ID_INFO)
        channel_bot = self.bot.get_channel(config.CHANNEL_ID_BOT)

        # Check for Empty User
        if not user:
            await self.bot.say("**Error**: Missing required <user>.")
            return

        # Try switching the roles
        try:
            await self.bot.replace_roles(user, *new_roles)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel,
                                        "{0.mention}, there was an error changing user's role. "
                                        "".format(ctx.message.author) + str(e))
            return

        # Set username
        username = user.nick if (user.nick is not None) else user.name

        # Approval message in Lobby
        await self.bot.say('**{1}** has successfully been made a **Comrade**!'.format(ctx.message.author, username))

        # Welcome Message in General
        await self.bot.send_message(channel_general, "Welcome our newest comrade, {0.mention}! Be sure to take a "
                                                     "look at {1.mention} for more, including a list of roles (pronouns"
                                                     ", colors, opt-in channels, etc) that you can join in {2.mention}."
                                                     " And feel free to DM a staffer if you need help or have any "
                                                     "questions.".format(user, channel_info, channel_bot))

        # Secondary Welcome DM to User
        wmsg = "Congratulations {0.mention}! You're now officially a comrade! Now that you have access to the main " \
               "server check out the {1.mention} channel for details on the different **roles** you can join. Some " \
               "are for pronouns, some give you access to private channels for recognized groups or private " \
               "interests, and some just give you a cool name color! When you're ready, head on over to the " \
               "{2.mention} channel and use `!join` or `!iam` to join your roles! \n\n If you have any questions, " \
               "feel free to ask a staff member. Thanks again, and welcome to LeftDisc!" \
               "".format(user, channel_info, channel_bot)

        # Send Private Welcome Message
        await self.bot.send_message(user, wmsg)

    # COMMAND: !psyops
    @commands.command(pass_context=True)
    @checks.is_staff()
    async def psyops(self, ctx, page: int = 1):
        """Lists the current Psyops/probationary users and their Join Date. 20 users per page."""

        # Get Variables
        server = ctx.message.server
        server_icon = str(server.icon_url)
        all_members = server.members
        role_probie = discord.utils.get(server.roles, name="Psyops")

        psyops_members_unsorted = [member for member in all_members if role_probie in member.roles]
        psyops_members = sorted(psyops_members_unsorted, key=lambda member: member.joined_at)

        start_index = (page - 1) * 20

        psyops_list = ""
        i = 1 + start_index

        if ((page - 1) * 20) >= len(psyops_members):
            await self.bot.say("**ERROR**: Page does not exist.")
            return

        for member in psyops_members[start_index:]:
            psyops_list += ("**" + str(i) + "**. {0.mention} - ".format(member) +
                            member.joined_at.strftime('%Y-%m-%d') + "\n")
            i += 1

            # Check for Break
            if i == (start_index + 21):
                break

        # print(psyops_list)

        # Create Embed Table
        embed = discord.Embed(title="Current Psyops Users: " + str(len(psyops_members)), colour=1315860,
                              description="Current probationary users and join dates.")
        embed.set_thumbnail(url=server_icon)
        embed.set_footer(text="Page {0}.     Staff User and Viewing Only!".format(str(page)))
        embed.add_field(name="Users", value=psyops_list, inline=False)

        await self.bot.say(embed=embed)

    # COMMAND !cleanup
    @commands.command(pass_context=True)
    @checks.is_admin()
    async def cleanup(self, ctx, certain: str = "n"):
        """Clears members in the Psyops group who have been in the server for more than 24 hours."""

        # Get Variables
        server = ctx.message.server
        all_members = server.members
        role_probie = discord.utils.get(server.roles, id=config.ROLE_ID_DEFAULT)
        psyops_members = [member for member in all_members if role_probie in member.roles]
        now = datetime.utcnow()

        total = 0

        for member in psyops_members:

            # Check Date Difference
            date_diff = now - member.joined_at
            days, seconds = date_diff.days, date_diff.seconds
            hours = (days * 24) + (seconds // 3600)

            if hours >= 24:
                if certain == "y":
                    await self.bot.kick(member)
                total += 1

        if certain == "n":
            await self.bot.say("**Total to be Purged**: " + str(total))
            return

        await self.bot.say("**Total Purged Users**: " + str(total))

    # COMMAND !setcounting
    @commands.command(pass_context=True)
    @checks.is_staff()
    async def setcounting(self, ctx, newcount: int):
        """For correcting counting. Sets current count and updates counting."""
        
        config.CURRENT_COUNT = newcount
        
        updated = config.update_counting()
        
        if updated:
            await self.bot.say("Current count set and stats updated.")
        else:
            await self.bot.say("**ERROR**: There was an error setting the count and updating the stats.")

    # COMMAND !updatecounting
    @commands.command(pass_context=True)
    @checks.is_staff()
    async def updatecounting(self, ctx):
        """Force updates counting."""

        updated = config.update_counting()

        if updated:
            await self.bot.say("Counting stats have been updated.")
        else:
            await self.bot.say("**ERROR**: Counting stats could not be updated.")



    # COMMAND !clip
    @commands.command(pass_context=True)
    @checks.is_staff()
    async def clip(self, ctx, channel: discord.Channel, message_id: str):
        """Manually clip and item when clipping fails for some reason."""
        
        # The message
        msg = await self.bot.get_message(channel, message_id)

        # Check for Message Already In
        if config.on_clipboard(msg.id):
            return

        # Set the Clipboard Channel
        clipboard = self.bot.get_channel(config.CHANNEL_ID_CLIPBOARD)

        # have to add a check here to make sure its not the pin board itself
        if channel == clipboard:
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

        clip_msg = await self.bot.send_message(clipboard, content="📋 - from {0.mention}".format(msg.channel), embed=embed)

        config.add_clipboard(msg.id, clip_msg.id)


def setup(bot):
    bot.add_cog(Staff(bot))
