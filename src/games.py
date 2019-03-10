import discord
from discord.ext import commands
from utils import checks
from utils import config


class Games:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !games
    @commands.group(invoke_without_command=True, pass_context=True)
    @checks.is_member()
    async def games(self, ctx, *, game_system: str = None):
        """Handles Games Profile Management."""

        # Are we using an allowed system?
        if game_system not in config.ALLOWED_GAME_SYSTEMS or game_system is None:
            await self.bot.say('Invalid roster command passed. Must be **list**, **add**, or **remove**; or a valid '
                               'game system must be passed to display a roster. Allowed system are: '
                               '```' + ", ".join(config.ALLOWED_GAME_SYSTEMS) + '```')
            return

        server = ctx.message.server

        # Create Variables for Embed Table
        result = config.get_game_profiles_by_system(game_system)

        if not result:
            await self.bot.say('There are no profiles for this game system.')

        accounts = ''
        names = ''
        i = 1

        for row in result:
            user = discord.utils.get(server.members, id=row['discord_id'])

            accounts += ('**' + str(i) + '**. ' + user.mention + '\n')
            names += ('**' + str(i) + '**. ' + row[game_system] + '\n')
            i += 1

        # Create Embed Table
        system_name = game_system.upper()
        embed = discord.Embed(title=system_name + " Roster", colour=9043968,
                              description="*Member Game Profiles for " + system_name + ".*")
        embed.add_field(name="Member", value=accounts, inline=True)
        embed.add_field(name="Game Data", value=names, inline=True)

        # Send Table to Channel
        await self.bot.send_message(ctx.message.channel, embed=embed)

    # COMMAND: !games list
    @games.command(name='list')
    async def roster_list(self):
        """Lists the allowed game system shorthands to use with the games profile commands."""

        # Return the list
        await self.bot.say("The allowed game systems for profiles are: ```"
                           + " \n".join(config.ALLOWED_GAME_SYSTEMS) + '```')

    # COMMAND: !games add
    @games.command(name='add', pass_context=True, aliases=['edit', 'update', 'insert'])
    async def roster_add(self, ctx, game_system: str, *, game_id: str = None):
        """Adds information to a game profile. Only one entry per system."""

        # Are we using an allowed system?
        if game_system not in config.ALLOWED_GAME_SYSTEMS:
            await self.bot.say('**ERROR**: Invalid game system given. Allowed system are: '
                               '```' + ", ".join(config.ALLOWED_GAME_SYSTEMS) + '```')
            return

        if game_id is None:
            await self.bot.say('**ERROR**: You must provide your game id/information.')
            return

        added = config.update_game_profile(ctx.message.author.id, game_system, game_id)

        # Return Success/Failure Message
        if added:
            await self.bot.say("{0.mention}, your game profile was successfully updated!".format(ctx.message.author))
        else:
            await self.bot.say("**ERROR**: There was a problem updating your game profile, {0.mention}."
                               .format(ctx.message.author))

    # COMMAND: !games remove
    @games.command(name='remove', pass_context=True, aliases=['delete'])
    async def roster_remove(self, ctx, game_system: str = None):
        """Remove a part of your game profile for a certain system."""

        # Are we using an allowed system?
        if game_system not in config.ALLOWED_GAME_SYSTEMS:
            await self.bot.say('**ERROR**: Invalid game system given. Allowed system are: '
                               '```' + ", ".join(config.ALLOWED_GAME_SYSTEMS) + '```')
            return

        added = config.remove_game_profile(ctx.message.author.id, game_system)

        # Return Success/Failure Message
        if added:
            await self.bot.say("{0.mention}, your game profile was successfully removed!".format(ctx.message.author))
        else:
            await self.bot.say("**ERROR**: There was a problem removing your game profile, {0.mention}."
                               .format(ctx.message.author))


def setup(bot):
    bot.add_cog(Games(bot))
