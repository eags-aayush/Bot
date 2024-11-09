import discord
from discord.ext import commands
import re
import asyncio
from datetime import timedelta

# Define the ban command
@commands.command(name="ban")
@commands.has_permissions(ban_members=True)  # Ensure the user has the 'ban_members' permission
async def ban_member(ctx, member: discord.Member, duration: str = None):

    """
    Bans a user.
    Usage:
    - !ban <username> -> Bans a specified user
    - !ban <username> <duration> -> Bans a specified user for a specified duration (1m, 1h, 1d, etc)
    """

    # Ensure the bot has permission to ban members
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("I don't have the required permission to ban members.")
        return

    moderator_role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if moderator_role and moderator_role.position >= ctx.author.top_role.position:
        await ctx.send("You don't have the required role to use this command.")
        return

    # If no duration is provided, ban the member permanently
    if duration is None:
        try:
            await member.ban(reason="Permanent ban by bot.")
            await ctx.send(f"{member.mention} has been permanently banned.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this member.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while trying to ban the member: {e}")
        return

    # If a duration is provided, parse the duration (e.g. "1h", "2d", "30m")
    time_pattern = re.compile(r'(\d+)([smhd])')
    matches = time_pattern.findall(duration.lower())

    if not matches:
        await ctx.send("Please provide a valid duration (e.g. 1h, 30m, 2d, 45s).")
        return

    # Convert the duration to seconds
    ban_duration = 0
    for match in matches:
        time_value, time_unit = match
        if time_unit == 's':
            ban_duration += int(time_value)
        elif time_unit == 'm':
            ban_duration += int(time_value) * 60
        elif time_unit == 'h':
            ban_duration += int(time_value) * 3600
        elif time_unit == 'd':
            ban_duration += int(time_value) * 86400  # 86400 seconds in a day

    # Ban the member temporarily for the given duration
    try:
        await member.ban(reason=f"Temporary ban for {duration} by bot.")
        await ctx.send(f"{member.mention} has been banned temporarily for {duration}.")
        
        # Set up a task to unban the member after the timeout duration
        await asyncio.sleep(ban_duration)  # Wait for the specified time duration
        await ctx.guild.unban(member)  # Unban the user after the timeout duration
        await ctx.send(f"{member.mention} has been unbanned after the temporary ban.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to ban this member.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while trying to ban the member: {e}")
