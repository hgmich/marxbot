import discord
from discord.ext import commands
import datetime


class Staff:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # STAFF-ONLY BOT COMMANDS ********************** #
    # ********************************************** #

    # Load Extension

    @commands.command(pass_context=True)
    @commands.has_role("admins!!!")
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
    @commands.has_role("admins!!!")
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""

        self.bot.unload_extension(extension_name)
        await self.bot.say("{} unloaded.".format(extension_name))

    # COMMAND: !setplaying
    @commands.command()
    @commands.has_any_role("admins!!!", "mods? mods! mods!?")
    async def setplaying(self, *, game_name: str):
        """Sets Karl's currently playing game."""

        await self.bot.change_presence(game=discord.Game(name=game_name))
        await self.bot.say("I just started playing this game, **{0}**! You should try it!".format(game_name))

    # COMMAND: !comrade
    @commands.command(pass_context=True)
    @commands.has_any_role("admins!!!", "mods? mods! mods!?")
    async def comrade(self, ctx, user: discord.Member):
        """Promotes a Psyop to a Comrade granting full server access."""

        # User to make Comrade
        # user = discord.utils.get(ctx.message.server.members, name=username)
        role_probie = discord.utils.get(ctx.message.server.roles, name="Psyops")
        role_comrade = discord.utils.get(ctx.message.server.roles, name="Comrades")

        new_roles = [role_comrade if x == role_probie else x for x in user.roles]

        channel_general = self.bot.get_channel('338594020101980160')

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

        # Success Message
        username = user.nick if (user.nick is not None) else user.name
        await self.bot.say('{0.mention}, **{1}** has successfully been made a **Comrade**!'
                           ''.format(ctx.message.author, username))
        await self.bot.send_message(channel_general, "Welcome our newest comrade, {0.mention}!".format(user))

    # COMMAND: !psyops
    @commands.command(pass_context=True)
    @commands.has_any_role("admins!!!", "mods? mods! mods!?")
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
    @commands.has_any_role("admins!!!", "mods? mods! mods!?")
    async def cleanup(self, ctx, certain: str = "n"):
        """Clears members in the Psyops group who have been in the server for more than 24 hours."""

        # Get Variables
        server = ctx.message.server
        all_members = server.members
        role_probie = discord.utils.get(server.roles, name="Psyops")
        psyops_members = [member for member in all_members if role_probie in member.roles]
        now = datetime.datetime.utcnow()

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


def setup(bot):
    bot.add_cog(Staff(bot))
