import discord
from discord.ext import commands
from utils import checks
from utils import config

class Roles:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # ROLES BOT COMMANDS *************************** #
    # ********************************************** #

    # COMMAND: !roles
    @commands.command(name='roles', pass_context=True, aliases=['listroles'])
    @checks.is_member()
    async def list_roles(self, ctx):
        """Generates a list of joinable roles."""

        allowed_types = ["Pronoun", "Private", "Region", "Interest", "Game", "Color"]

        # Setup Message
        message = "Below is a list of roles you may join. Please see the info channel for more details.\n"

        # Add Groups
        for role_type in allowed_types:

            # Set List Heading and Start
            message += "\n**" + role_type + " Roles**\n```\n"

            # Get Roles
            type_roles = config.get_roles_by_type(role_type.lower())

            # Loop Through Roles in that Type
            for role in type_roles:
                message += role + "\n"

            # Finalize Message
            message += "```"

        await self.bot.say(message)

    # COMMAND: !join
    @commands.command(name='join', pass_context=True, aliases=['iam'])
    @checks.is_member()
    async def join_group(self, ctx, *, role_name: str):
        """Join a group or obtain a specific role."""

        # Get User and Server
        user = ctx.message.author
        server = ctx.message.server

        # Try to get the Role ID
        role_id = config.get_role_id_from_lowername(role_name.lower())

        # Check for Allowed Role
        if role_id is None:
            await self.bot.say("{0.mention}, you must select one of the public groups to join. Use `!roles` for a list "
                               "of roles members may join".format(user))
            return

        # Try to Grant the Role
        try:
            role = discord.utils.get(server.roles, id=role_id)
            await self.bot.add_roles(user, role)
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error updating your roles. **Error**: ".format(user) + str(e))
            return

        # Get Role Name from ID
        role_name_full = config.get_role_name_from_id(role_id)

        # Success Message
        await self.bot.say(
            "{0.mention}, you have been given the role **{1}**.".format(user, role_name_full))

    # COMMAND: !leave
    @commands.command(name='leave', pass_context=True, aliases=['iamnot'])
    @checks.is_member()
    async def leave_group(self, ctx, *, role_name: str):
        """Leave a group or remove a specific role."""

        # Get User and Server
        user = ctx.message.author
        server = ctx.message.server

        # Try to get the Role ID
        role_id = config.get_role_id_from_lowername(role_name.lower())

        # Check for Allowed Role
        if role_id is None:
            await self.bot.say("{0.mention}, you must select one of the public groups to leave.".format(user))
            return

        # Try to Remove the Role
        try:
            role = discord.utils.get(server.roles, id=role_id)
            await self.bot.remove_roles(user, role)
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error updating your roles. **Error**: ".format(user) + str(e))
            return

        # Get Role Name from ID
        role_name_full = config.get_role_name_from_id(role_id)

        # Success Message
        await self.bot.say(
            "{0.mention}, your **{1}** role has been removed.".format(user, role_name_full))


def setup(bot):
    bot.add_cog(Roles(bot))
