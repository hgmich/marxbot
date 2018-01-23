import discord
from discord.ext import commands
import random


class Roles:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # ROLES BOT COMMANDS *************************** #
    # ********************************************** #

    # COMMAND: !join
    @commands.command(name='join', pass_context=True, aliases=['iam'])
    @commands.has_role("Comrades")
    async def join_group(self, ctx, *, group_name: str):
        """Join a group or obtain a specific role."""

        # Get User and Server
        user = ctx.message.author
        server = ctx.message.server

        # Define Allowed Groups
        allowed_roles = ['queer',
                         'not a man',
                         'mental health',
                         'poc',
                         'person of color',
                         'relationships',
                         'they/them',
                         'they',
                         'them',
                         'she/her',
                         'she',
                         'her',
                         'he/him',
                         'he',
                         'him',
                         'africa',
                         'asia',
                         'eu',
                         'europe',
                         'na',
                         'north america',
                         'oce',
                         'oceania',
                         'sa',
                         'south america',
                         'destiny (pc)',
                         'destiny (psn)',
                         'destiny (xbl)',
                         'lol',
                         'league of legends',
                         'ow (pc)',
                         'ow (psn)',
                         'ow (xbl)',
                         'overwatch (pc)',
                         'overwatch (psn)',
                         'overwatch (xbl)',
                         'pubg',
                         'r6s (pc)',
                         'rainbow six siege (pc)',
                         'movie night',
                         'stream alerts']

        # ROLE MATCH DICTIONARY
        role_dictionary = {"queer": "Queer",
                           "not a man": "Not a Man",
                           "mental health": "Mental Health",
                           "poc": "Person of Color",
                           "person of color": "Person of Color",
                           "relationships": "Relationships",
                           "they/them": "They/Them",
                           "they": "They/Them",
                           "them": "They/Them",
                           "she/her": "She/Her",
                           "she": "She/Her",
                           "her": "She/Her",
                           "he/him": "He/Him",
                           "he": "He/Him",
                           "him": "He/Him",
                           "africa": "Africa",
                           "asia": "Asia",
                           "eu": "Europe",
                           "europe": "Europe",
                           "na": "North America",
                           "north america": "North America",
                           "oce": "Oceania",
                           "oceania": "Oceania",
                           "sa": "South America",
                           "south america": "South America",
                           "destiny (pc)": "Destiny (PC)",
                           "destiny (psn)": "Destiny (PSN)",
                           "destiny (xbl)": "Destiny (XBL)",
                           "lol": "League of Legends",
                           "league of legends": "League of Legends",
                           "ow (pc)": "Overwatch (PC)",
                           "ow (psn)": "Overwatch (PSN)",
                           "ow (xbl)": "Overwatch (XBL)",
                           "overwatch (pc)": "Overwatch (PC)",
                           "overwatch (psn)": "Overwatch (PSN)",
                           "overwatch (xbl)": "Overwatch (XBL)",
                           "pubg": "PUBG",
                           "r6s (pc)": "Rainbow Six Siege (PC)",
                           "rainbow six siege (pc)": "Rainbow Six Siege (PC)",
                           "movie night": "Movie Night",
                           "stream alerts": "Stream Alerts"}

        # Check for Allowed Role
        if group_name.lower() not in allowed_roles:
            await self.bot.say("{0.mention}, you must select one of the public groups to join.".format(user))
            return

        # Try to Grant the Role
        try:
            role = discord.utils.get(server.roles, name=role_dictionary[group_name.lower()])
            await self.bot.add_roles(user, role)
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error updating your roles. **Error**: ".format(user) + str(e))
            return

        # Success Message
        await self.bot.say(
            "{0.mention}, you have been given the role **{1}**.".format(user, role_dictionary[group_name.lower()]))

    # COMMAND: !leave
    @commands.command(name='leave', pass_context=True, aliases=['iamnot'])
    @commands.has_role("Comrades")
    async def leave_group(self, ctx, *, group_name: str):
        """Leave a group or remove a specific role."""

        # Get User and Server
        user = ctx.message.author
        server = ctx.message.server  # Define Allowed Groups
        allowed_roles = ['queer',
                         'not a man',
                         'mental health',
                         'poc',
                         'person of color',
                         'relationships',
                         'they/them',
                         'they',
                         'them',
                         'she/her',
                         'she',
                         'her',
                         'he/him',
                         'he',
                         'him',
                         'africa',
                         'asia',
                         'eu',
                         'europe',
                         'na',
                         'north america',
                         'oce',
                         'oceania',
                         'sa',
                         'south america',
                         'destiny (pc)',
                         'destiny (psn)',
                         'destiny (xbl)',
                         'lol',
                         'league of legends',
                         'ow (pc)',
                         'ow (psn)',
                         'ow (xbl)',
                         'overwatch (pc)',
                         'overwatch (psn)',
                         'overwatch (xbl)',
                         'pubg',
                         'r6s (pc)',
                         'rainbow six siege (pc)',
                         'movie night',
                         'stream alerts']

        # ROLE MATCH DICTIONARY
        role_dictionary = {"queer": "Queer",
                           "not a man": "Not a Man",
                           "mental health": "Mental Health",
                           "poc": "Person of Color",
                           "person of color": "Person of Color",
                           "relationships": "Relationships",
                           "they/them": "They/Them",
                           "they": "They/Them",
                           "them": "They/Them",
                           "she/her": "She/Her",
                           "she": "She/Her",
                           "her": "She/Her",
                           "he/him": "He/Him",
                           "he": "He/Him",
                           "him": "He/Him",
                           "africa": "Africa",
                           "asia": "Asia",
                           "eu": "Europe",
                           "europe": "Europe",
                           "na": "North America",
                           "north america": "North America",
                           "oce": "Oceania",
                           "oceania": "Oceania",
                           "sa": "South America",
                           "south america": "South America",
                            "destiny (pc)": "Destiny (PC)",
                           "destiny (psn)": "Destiny (PSN)",
                           "destiny (xbl)": "Destiny (XBL)",
                           "lol": "League of Legends",
                           "league of legends": "League of Legends",
                           "ow (pc)": "Overwatch (PC)",
                           "ow (psn)": "Overwatch (PSN)",
                           "ow (xbl)": "Overwatch (XBL)",
                           "overwatch (pc)": "Overwatch (PC)",
                           "overwatch (psn)": "Overwatch (PSN)",
                           "overwatch (xbl)": "Overwatch (XBL)",
                           "pubg": "PUBG",
                           "r6s (pc)": "Rainbow Six Siege (PC)",
                           "rainbow six siege (pc)": "Rainbow Six Siege (PC)",
                           "movie night": "Movie Night",
                           "stream alerts": "Stream Alerts"}

        # Check for Allowed Role
        if group_name.lower() not in allowed_roles:
            if "mod" in group_name.lower():
                await self.bot.say("{0.mention}, if you try to make yourself a mod too much we might have to "
                                   "send you to the gulags.".format(user))
                return
            else:
                await self.bot.say("{0.mention}, you must select one of the public groups to leave.".format(user))
                return

        # Try to Grant the Role
        try:
            role = discord.utils.get(server.roles, name=role_dictionary[group_name.lower()])
            await self.bot.remove_roles(user, role)
        except Exception as e:
            await self.bot.say(
                "{0.mention}, there was an error updating your roles. **Error**: ".format(user) + str(e))
            return

        # Success Message
        await self.bot.say(
            "{0.mention}, your **{1}** role has been removed.".format(user, role_dictionary[group_name.lower()]))


def setup(bot):
    bot.add_cog(Roles(bot))
