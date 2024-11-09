import discord
from discord.ext import commands
from events.on_member_join import on_member_join as member_join_event
from events.on_member_leave import on_member_leave as member_leave_event
from commands.nick import change_nickname
from commands.purge import purge_msg
from commands.kick import kick_member
from commands.timeout import timeout_member
from commands.ban import ban_member
from commands.role import role_assign
from commands.ticket import ticket, ticket_close
from commands.giveaway import init_db, start_giveaway, reroll_giveaway, cancel_giveaway, start_check_giveaways
from commands.autoresponder import add_autoresponder, remove_autoresponder, auto_responder

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("--------------------------------")
    start_check_giveaways(bot)

@bot.event
async def on_member_join(member):
    await member_join_event(member)

@bot.event
async def on_member_leave(member):
    await member_leave_event(member)

@bot.command(name="giveaway_start")
@commands.has_permissions(administrator=True)
async def giveaway_start(ctx, prize: str, duration: str, winners_count: int):
    await start_giveaway(ctx, prize, duration, winners_count)

@bot.command(name="giveaway_reroll")
@commands.has_permissions(administrator=True)
async def giveaway_reroll(ctx, message_id: int):
    await reroll_giveaway(bot, ctx, message_id)

@bot.command(name="giveaway_cancel")
@commands.has_permissions(administrator=True)
async def giveaway_cancel(ctx, message_id: int):
    await cancel_giveaway(ctx, message_id)

@bot.event
async def on_message(message):
    await auto_responder(message)
    await bot.process_commands(message)  # Ensure other commands are processed

bot.add_command(change_nickname)
bot.add_command(purge_msg)
bot.add_command(kick_member)
bot.add_command(timeout_member)
bot.add_command(ban_member)
bot.add_command(role_assign)
bot.add_command(ticket)
bot.add_command(ticket_close)
bot.add_command(add_autoresponder)
bot.add_command(remove_autoresponder)

# Initialize the database
init_db()

# Run the bot
bot.run("MTMwMzk0MjYwODUwNjMyNzA5MQ.G_1uHO.Kus4NojJmVXw_BAraGPlOZg2rTijxnMOAGT2Bo")
