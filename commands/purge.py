import discord
from discord.ext import commands

# Define the purge command
@commands.command(name="purge")
async def purge_msg(ctx, amount: int):

    """
    Delets messages in mass
    Usage:
    - !purge <amount> -> Delete specified amount of messages
    """

    # Ensure the bot has the necessary permissions
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You don't have the required permissions to use this command.")
        return

    # Check if the user has the 'Moderator' role or a higher role
    moderator_role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if moderator_role and moderator_role.position >= ctx.author.top_role.position:
        await ctx.send("You don't have the required role to use this command.")
        return

    # Check if the amount is a valid number and greater than 0
    if amount <= 0:
        await ctx.send("Please specify a number greater than 0.")
        return

    # Purge the specified number of messages
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command itself
        await ctx.send(f"Deleted {len(deleted) - 1} messages.", delete_after=5)  # -1 to not count the command message
    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages in this channel.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while trying to delete messages: {e}")
