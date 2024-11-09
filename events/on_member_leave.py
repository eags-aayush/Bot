import discord
async def on_member_leave(member):
    leave_channel_name = "leave"
    leave_channel = discord.utils.get(member.guild.text_channels, name=leave_channel_name)
    if leave_channel:
        await leave_channel.send(f"BDSK chala gya **{member.mention}**!")
    try:
        await member.send(f"We're sad to see you go from **{member.guild.name}**. Take care!")
    except discord.Forbidden:
        print(f"Could not send farewell DM to {member.name}.")
