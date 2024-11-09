import discord
from discord.ext import commands

# Define the role management command
async def role_assign(ctx, member: discord.Member, *, role_name: str = None):
    """
    Assigns or removes roles for a user.
    Usage:
    - !role <username> <role> -> Assigns the specified role
    - !role <username> -> Removes all roles from the user (except @everyone)
    """
    
    # Check if the author has a role higher than "Moderator"
    author_top_role = ctx.author.top_role
    moderator_role = discord.utils.get(ctx.guild.roles, name="Moderator")

    if moderator_role is None:
        await ctx.send("The 'Moderator' role does not exist in this server.")
        return

    if author_top_role <= moderator_role:
        await ctx.send("You do not have permission to use this command.")
        return

    if role_name is None:
        # If no role is specified, remove all roles from the member (except @everyone)
        try:
            roles_to_remove = [role for role in member.roles if role != ctx.guild.default_role]
            await member.remove_roles(*roles_to_remove)
            await ctx.send(f"All roles have been removed from {member.mention}.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to remove roles for this user.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")
        return

    # Find the role in the server
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if not role:
        await ctx.send(f"Role '{role_name}' not found.")
        return

    # Check if the bot has permission to assign this role
    if ctx.guild.me.top_role <= role:
        await ctx.send("I do not have permission to assign this role.")
        return

    try:
        # Add the role to the member
        await member.add_roles(role)
        await ctx.send(f"Successfully assigned the role '{role_name}' to {member.mention}.")
    except discord.Forbidden:
        await ctx.send("I do not have permission to modify roles for this user.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")

# Create the command object
role_assign = commands.Command(role_assign, name="role")
