from discord.ext import commands
import discord.utils
import settings


# Check for Role
def check_role(ctx, check):
    msg = ctx.message
    ch = msg.channel
    author = msg.author

    if ch.is_private:
        return False

    role = discord.utils.find(check, author.roles)
    return role is not None


# Check for Staff
def is_staff():
    def predicate(ctx):
        return check_role(ctx, lambda r: r.id in (settings.ROLE_ID_ADMIN, settings.ROLE_ID_MOD))

    return commands.check(predicate)


# Check for Admins
def is_admin():
    def predicate(ctx):
        return check_role(ctx, lambda r: r.id == settings.ROLE_ID_ADMIN)

    return commands.check(predicate)


# Check for Moderators
def is_mod():
    def predicate(ctx):
        return check_role(ctx, lambda r: r.id == settings.ROLE_ID_MOD)

    return commands.check(predicate)


# Check for Comrade/Member
def is_member():
    def predicate(ctx):
        return check_role(ctx, lambda r: r.id == settings.ROLE_ID_MEMBER)

    return commands.check(predicate)
