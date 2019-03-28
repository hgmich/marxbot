import discord
from discord.ext import commands
from utils import checks
from utils import config
import datetime


class Events:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !events
    @commands.group(invoke_without_command=True, pass_context=True)
    @checks.is_member()
    async def events(self, ctx):
        """Handles Events Management. Displays list of upcoming events in the calendar without command passed."""

        server = ctx.message.server

        # Get Calendar Events
        events = config.get_events_in_calendar()

        if not events:
            await self.bot.say('There are currently no upcoming events in the calendar.')
            return

        # Setup the Embed
        embed = discord.Embed(title="LeftDisc Events Calendar", colour=9043968)

        for event in events:
            creator = discord.utils.get(server.members, id=event['planner_id'])
            desc = event['description'] + " \n **Host**: " + creator.mention + ", (ID: " + str(event['event_id']) + ")"
            embed.add_field(name=event['event_date'], value=desc)

        # Send Calendar to Channel
        await self.bot.send_message(ctx.message.channel, embed=embed)

    # COMMAND !events addrole
    @events.command(name='addrole', pass_context=True)
    @checks.is_member()
    @checks.can_use_events()
    async def add_event_role(self, ctx, *, event_role_name: str):
        """Creates a joinable, pingable role for an event. Roles are purged after two weeks."""

        # Check to see if the role is a substring of existing roles to prevent unjoinable/deletable roles
        existing_roles = config.get_event_roles()

        for name in existing_roles:
            if event_role_name in name:
                await self.bot.say("**ERROR**: This role name is too close to another event role. Please choose a "
                                   "different role name.")
                return

        # Server
        server = ctx.message.server

        # Member
        member = ctx.message.author

        # Setup No Permissions
        perms = discord.Permissions().none()

        # Create the Role
        role = await self.bot.create_role(server, name=event_role_name, mentionable=True, permissions=perms)

        # Get Date
        today = datetime.date.today().strftime('%Y-%m-%d')

        # Make Sure the Role was Created
        if role is None:
            await self.bot.say("**ERROR**: There was an error creating the role.")
            return

        # Add the Role to the Event List
        added = config.add_event_role(role.id, event_role_name, member.id, today)

        # Return Success/Failure Message
        if added:
            await self.bot.say("The event role has been successfully created.")
        else:
            await self.bot.delete_role(server, role)
            await self.bot.say("**ERROR**: The event role could not be created.")

    # COMMAND !events removerole
    @events.command(name='removerole', pass_context=True)
    @checks.is_member()
    @checks.can_use_events()
    async def remove_event_role(self, ctx, *, event_role_name: str):
        """Allows the creator of an event role to delete it."""

        # Server
        server = ctx.message.server

        # Member
        member = ctx.message.author

        # Get the Role
        role_info = config.get_event_role_info(event_role_name)

        # Make Sure the Role Exists
        if not role_info or role_info is None:
            await self.bot.say("**ERROR**: No event role exists with that name.")
            return

        # Check for many roles
        if role_info == "many":
            await self.bot.say("**ERROR**: There are many event roles that match that name. You must be more specific.")
            return

        # Make sure the creator is the one trying to delete the role
        if member.id != role_info['creator_id']:
            await self.bot.say("**ERROR**: Only the creator of the event role can delete it.")
            return

        # Remove the Role from the Event Roles
        removed = config.remove_event_role(role_info['role_id'])

        # Return Success/Failure Message
        if removed:
            # Get the Role
            role = discord.utils.get(server.roles, id=role_info['role_id'])

            # Delete the Role
            await self.bot.delete_role(server, role)

            await self.bot.say("The event role was successfully deleted.")
        else:
            await self.bot.say("**ERROR**: The event role could not be deleted.")

    # COMMAND !events roles
    @events.command(name='roles', pass_context=True)
    @checks.is_member()
    async def list_event_roles(self, ctx):
        """Lists the available event roles."""

        # Get Roles List
        roles = config.get_event_roles()
        roles.sort()

        # Setup Message
        message = "Below is a list of current event roles you may join. Use `!events join <role>` to join the role." \
                  " \n```\n"

        # Loop Through Roles in that Type
        for role in roles:
            message += role + "\n"

        # Finalize Message
        message += "```"

        await self.bot.say(message)

        await self.bot.delete_message(ctx.message)

    # COMMAND !events join
    @events.command(name='join', pass_context=True)
    @checks.is_member()
    async def join_event_role(self, ctx, *, event_role_name: str):
        """Allows members to join an event role to receive pings and updates from the event planner."""

        # Server
        server = ctx.message.server

        # Member
        member = ctx.message.author

        # Get Role Info
        role_info = config.get_event_role_info(event_role_name)

        # Make Sure the Role Exists
        if not role_info or role_info is None:
            await self.bot.say("**ERROR**: No event role exists with a name like that.")
            return

        if role_info == "many":
            await self.bot.say("**ERROR**: There are many event roles that match that name. You must be more specific.")
            return

        # Get the Role
        role = discord.utils.get(server.roles, id=role_info['role_id'])

        # Try to Grant the Role
        try:
            await self.bot.add_roles(member, role)
            await self.bot.say(
                "{0.mention}, you have successfully joined the event role **{1}**."
                "".format(member, role_info['role_name']))
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error giving you the event role. **Error**: ".format(member) + str(e))

    # COMMAND !events leave
    @events.command(name='leave', pass_context=True)
    @checks.is_member()
    async def leave_event_role(self, ctx, *, event_role_name: str):
        """Allows members to join an event role to receive pings and updates from the event planner."""

        # Server
        server = ctx.message.server

        # Member
        member = ctx.message.author

        # Get Role Info
        role_info = config.get_event_role_info(event_role_name)

        # Make Sure the Role Exists
        if not role_info or role_info is None:
            await self.bot.say(
                "**ERROR**: No event role exists with a name like that.")
            return

        if role_info == "many":
            await self.bot.say("**ERROR**: There are many event roles that match that name. You must be more specific.")
            return

        # Get the Role
        role = discord.utils.get(server.roles, id=role_info['role_id'])

        # Try to Grant the Role
        try:
            await self.bot.remove_roles(member, role)
            await self.bot.say(
                "{0.mention}, you have successfully left the event role **{1}**."
                "".format(member, role_info['role_name']))
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error removing the event role. **Error**: ".format(member) + str(e))

    # COMMAND !events tagged
    @events.command(name='tagged', pass_context=True)
    @checks.is_member()
    async def list_members_in_event_role(self, ctx, *, event_role_name: str):
        """Lists the users who have joined the event role."""

        # Get Roles List
        role_info = config.get_event_role_info(event_role_name)

        # Make Sure the Role Exists
        if not role_info or role_info is None:
            await self.bot.say(
                "**ERROR**: No event role exists with a name like that.")
            return

        if role_info == "many":
            await self.bot.say("**ERROR**: There are many event roles that match that name. You must be more specific.")
            return

        # Set Server
        server = ctx.message.server

        # Get Role ID
        role_id = role_info['role_id']

        # Get Actual Role
        event_role = discord.utils.get(server.roles, id=role_id)

        role_members = []

        # Get List of Users
        for member in server.members:
            for role in member.roles:
                if role == event_role:
                    role_members.append(member.display_name)

        if not role_members:
            await self.bot.say("No users have joined this event role.")
            return

        role_members.sort()

        # Setup Message
        message = "Here is a list of users who have joined the event role **" + role_info['role_name'] + "**:" \
                  " \n```\n"

        for m in role_members:
            message += m + "\n"

        message += "```"

        await self.bot.say(message)

        await self.bot.delete_message(ctx.message)

    # COMMAND !events addcal
    @events.command(name='addcal', pass_context=True)
    @checks.is_member()
    @checks.can_use_events()
    async def add_event_to_events_calendar(self, ctx, event_date: str = None, *, event_description: str = None):
        """Adds an event to the public events calendar."""

        if event_date is None or event_description is None:
            await self.bot.say("**ERROR**: You must include a date in YYYY-MM-DD format and an event description.")
            return

        try:
            datetime.datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            await self.bot.say("**ERROR**: Your date must be valid and in YYYY-MM-DD format.")
            return

        # Member
        member = ctx.message.author

        # Add the Event to the Event Calendar
        added = config.add_event_calendar(member.id, event_date, event_description)

        # Return Success/Failure Message
        if added:
            await self.bot.say(member.mention + ", your event has been added to the calendar. If you have created an "
                                                "event role, please make sure you include that role in your calendar "
                                                "description! Use `!events editcal <event_id>` to edit your calendar "
                                                "entry if you need to.")
        else:
            await self.bot.say("**ERROR**: " + member.mention + ", your event could not be added to the calendar.")

    # COMMAND !events editcal
    @events.command(name='editcal', pass_context=True)
    @checks.is_member()
    @checks.can_use_events()
    async def edit_event_calendar_event(self, ctx, event_id: int = None, event_date: str = None, *, event_description: str = None):
        """Allows the host of a calendar event to edit the event details."""

        if event_id is None or event_date is None or event_description is None:
            await self.bot.say("**ERROR**: You must use the event id, a date in YYYY-MM-DD format, and an event "
                               "description.")
            return

        try:
            datetime.datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            await self.bot.say("**ERROR**: Your date must be valid and in YYYY-MM-DD format.")
            return

        # Member
        member = ctx.message.author

        # Get the Role
        event_info = config.get_calendar_event(event_id)

        # Make Sure the Event Exists
        if not event_info:
            await self.bot.say("**ERROR**: No event is on the calendar with that ID.")
            return

        # Make sure the creator is the one trying to delete the role
        if member.id != event_info['planner_id']:
            await self.bot.say("**ERROR**: Only the creator of the calendar event can edit it.")
            return

        # Update the Event
        updated = config.update_event_calendar(event_id, event_date, event_description)

        # Return Success/Failure Message
        if updated:
            await self.bot.say(member.mention + ", your event has been updated on the calendar.")
        else:
            await self.bot.say(
                "**ERROR**: " + member.mention + ", your event could not be updated on the calendar.")

    # COMMAND !events removecal
    @events.command(name='removecal', pass_context=True)
    @checks.is_member()
    @checks.can_use_events()
    async def remove_event_from_events_calendar(self, ctx, event_id: int):
        """Allows the host of a calendar event to remove it from the calendar."""

        # Member
        member = ctx.message.author

        # Get the Role
        event_info = config.get_calendar_event(event_id)

        # Make Sure the Event Exists
        if not event_info:
            await self.bot.say("**ERROR**: No event is on the calendar with that ID.")
            return

        # Make sure the creator is the one trying to delete the role
        if member.id != event_info['planner_id']:
            await self.bot.say("**ERROR**: Only the creator of the calendar event can delete it.")
            return

        # Remove the Event from the Event Calendar
        removed = config.remove_event_calendar(event_id)

        # Return Success/Failure Message
        if removed:
            await self.bot.say(member.mention + ", your event has been removed from the calendar.")
        else:
            await self.bot.say("**ERROR**: " + member.mention + ", your event could not be removed from the calendar.")


def setup(bot):
    bot.add_cog(Events(bot))
