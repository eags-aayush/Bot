import discord
from discord.ext import commands

# Define the `nick` command
@commands.command(name="nick")
async def change_nickname(ctx, member: discord.Member = None, *, new_nickname: str = None):

    """
    Assigns a nickname for a user.
    Usage:
    - !nick <username> <role> -> Assigns a nickname to the specified user
    """

    # If no member is mentioned, use the author (the user who sent the command)
    if member is None:
        member = ctx.author

    # If no new nickname is provided, return an error
    if new_nickname is None:
        await ctx.send("Please provide a new nickname.")
        return

    try:
        # Check if the bot has permission to change the user's nickname
        if ctx.guild.me.guild_permissions.manage_nicknames:
            await member.edit(nick=new_nickname)
            await ctx.send(f"{member.mention}'s nickname has been changed to: {new_nickname}")
        else:
            await ctx.send("I don't have permission to change nicknames.")
    except discord.Forbidden:
        await ctx.send("I couldn't change the nickname due to permissions.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
