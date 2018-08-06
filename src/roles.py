import discord
from discord.ext import commands
import json
import os


class Roles:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # ROLES BOT COMMANDS *************************** #
    # ********************************************** #

    # COMMAND: !roles
    @commands.command(name='roles', pass_context=True, aliases=['listroles'])
    @commands.has_role("Comrades")
    async def list_roles(self, ctx):
        """Generates a list of joinable roles."""

        # Get the JSON file thing.
        file_path = os.path.normpath("{0}/roles.json".format(
            os.path.dirname(os.path.realpath(__file__))
        ))

        with open(file_path, 'r') as file:
            roles_dict = json.loads(file.read())

        # Setup Message
        message = "Below is a list of roles you may join.\n ```\n"

        # Add Groups
        for x in (sorted(set(roles_dict.values()))):
            message += x + "\n"

        # Finalize Message
        message += "```"

        await self.bot.say(message)

    # COMMAND: !join
    @commands.command(name='join', pass_context=True, aliases=['iam'])
    @commands.has_role("Comrades")
    async def join_group(self, ctx, *, group_name: str):
        """Join a group or obtain a specific role."""

        # Get User and Server
        user = ctx.message.author
        server = ctx.message.server

        # Get the JSON file thing.
        file_path = os.path.normpath("{0}/roles.json".format(
            os.path.dirname(os.path.realpath(__file__))
        ))

        with open(file_path, 'r') as file:
            roles_dict = json.loads(file.read())

        # Check for Allowed Role
        if group_name.lower() not in roles_dict:
            await self.bot.say("{0.mention}, you must select one of the public groups to join.".format(user))
            return

        # Try to Grant the Role
        try:
            role = discord.utils.get(server.roles, name=roles_dict[group_name.lower()])
            await self.bot.add_roles(user, role)
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error updating your roles. **Error**: ".format(user) + str(e))
            return

        # Success Message
        await self.bot.say(
            "{0.mention}, you have been given the role **{1}**.".format(user, roles_dict[group_name.lower()]))

    # COMMAND: !leave
    @commands.command(name='leave', pass_context=True, aliases=['iamnot'])
    @commands.has_role("Comrades")
    async def leave_group(self, ctx, *, group_name: str):
        """Leave a group or remove a specific role."""

        # Get User and Server
        user = ctx.message.author
        server = ctx.message.server

        # Get the JSON file thing.
        file_path = os.path.normpath("{0}/roles.json".format(
            os.path.dirname(os.path.realpath(__file__))
        ))

        with open(file_path, 'r') as file:
            roles_dict = json.loads(file.read())

        # Check for Allowed Role
        if group_name.lower() not in roles_dict:
            if "mod" in group_name.lower():
                await self.bot.say("{0.mention}, if you try to make yourself a mod too much we might have to "
                                   "send you to the gulags.".format(user))
                return
            else:
                await self.bot.say("{0.mention}, you must select one of the public groups to leave.".format(user))
                return

        # Try to Grant the Role
        try:
            role = discord.utils.get(server.roles, name=roles_dict[group_name.lower()])
            await self.bot.remove_roles(user, role)
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error updating your roles. **Error**: ".format(user) + str(e))
            return

        # Success Message
        await self.bot.say(
            "{0.mention}, your **{1}** role has been removed.".format(user, roles_dict[group_name.lower()]))


def setup(bot):
    bot.add_cog(Roles(bot))
