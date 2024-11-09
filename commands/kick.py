import discord
from discord.ext import commands

# Define the kick command
@commands.command(name="kick")
@commands.has_permissions(kick_members=True)  # Ensure the user has the permission to kick members
async def kick_member(ctx, member: discord.Member, *, reason=None):
    # Check if the bot has permission to kick the member

    """
    Kicks a user.
    Usage:
    - !kick <username> -> Kicks the specified user
    - !kick <username> <reason> -> Kicks the specified user with the specified reason
    """

    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("I don't have the required permission to kick members.")
        return

    # Ensure the target member is not higher or equal in role hierarchy
    moderator_role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if member.top_role.position >= ctx.author.top_role.position:
        await ctx.send("You cannot kick a member with a higher or equal role than you.")
        return

    # Kick the member and send a confirmation message
    try:
        await member.kick(reason=reason)
        await ctx.send(f"Successfully kicked {member.mention}. Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick that member.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while trying to kick the member: {e}")
