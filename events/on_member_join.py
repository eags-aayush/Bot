import discord
async def on_member_join(member):
    welcome_channel_name = "welcome"
    welcome_channel = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)
    if welcome_channel:
        await welcome_channel.send(f"Welcome to **{member.guild.name}**, {member.mention}! 🎉")
    try:
        await member.send(f"Welcome to **{member.guild.name}**! We're glad to have you here.")
    except discord.Forbidden:
        print(f"Could not send DM to {member.name}.")
