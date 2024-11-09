import discord
from discord.ext import commands
import re
import asyncio  # Add this import
from datetime import timedelta

# Define the timeout command
@commands.command(name="timeout")
async def timeout_member(ctx, member: discord.Member, duration: str = None):
    # Ensure the bot has permission to timeout 
    
    """
    Gives a specified amount of timeout to the specified user
    Usage:
    - !timeout <username> <time> -> Timeouts a specified user for a specified amount of time (1m, 1h, 1d, etc)

    - !timeout <username> <time> <reason> -> Timeouts a specified user for a specified amount of time with a valid reason (1m, 1h, 1d, etc)

    """

    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("I don't have the required permission to timeout members.")
        return

    # Check if the author has the required permissions (role higher than 'moderator')
    moderator_role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if moderator_role and moderator_role.position >= ctx.author.top_role.position:
        await ctx.send("You don't have the required role to use this command.")
        return

    # If no duration is provided, show an error message
    if duration is None:
        await ctx.send("Please specify a valid duration (e.g. 1m, 30s, 1h, 2d).")
        return

    # Parse the duration string (e.g., "1m", "2h", "30s")
    time_pattern = re.compile(r'(\d+)([smhd])')
    matches = time_pattern.findall(duration.lower())

    if not matches:
        await ctx.send("Please provide a valid duration (e.g. 1m, 30s, 2d).")
        return

    # Convert the duration to seconds
    timeout_duration = 0
    for match in matches:
        time_value, time_unit = match
        if time_unit == 's':
            timeout_duration += int(time_value)
        elif time_unit == 'm':
            timeout_duration += int(time_value) * 60
        elif time_unit == 'h':
            timeout_duration += int(time_value) * 3600
        elif time_unit == 'd':
            timeout_duration += int(time_value) * 86400  # 86400 seconds in a day

    # Timeout the member temporarily for the given duration
    try:
        await member.timeout(timedelta(seconds=timeout_duration), reason=f"Timeout for {duration} by bot.")
        await ctx.send(f"{member.mention} has been timed out for {duration}.")
        
        # Set up a task to remove the timeout after the specified duration
        await asyncio.sleep(timeout_duration)  # Wait for the specified time duration
        await member.remove_timeout()  # Remove the timeout after the specified time
        await ctx.send(f"{member.mention} has been removed from timeout after the specified duration.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to timeout this member.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while trying to timeout the member: {e}")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {e}")
