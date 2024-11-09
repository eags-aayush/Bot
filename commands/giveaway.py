import discord
from discord.ext import tasks
import sqlite3
import time
import random

# Global variable for the bot instance
bot_instance = None

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("giveaways.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS giveaways (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    guild_id TEXT NOT NULL,
                    prize TEXT NOT NULL,
                    host_id TEXT NOT NULL,
                    winners_count INTEGER NOT NULL,
                    end_time INTEGER NOT NULL,
                    status TEXT DEFAULT 'ongoing'
                )''')
    conn.commit()
    conn.close()

# Function to start a giveaway
async def start_giveaway(ctx, prize: str, duration: str, winners_count: int):
    time_multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    unit = duration[-1]
    if unit not in time_multiplier:
        await ctx.send("Invalid duration format. Use s (seconds), m (minutes), h (hours), or d (days).")
        return

    try:
        duration_seconds = int(duration[:-1]) * time_multiplier[unit]
    except ValueError:
        await ctx.send("Invalid duration format.")
        return

    end_time = int(time.time()) + duration_seconds

    # Create the giveaway embed
    embed = discord.Embed(title="🎉 Giveaway!", description=f"Prize: {prize}", color=0x00ff00)
    embed.add_field(name="Hosted by", value=ctx.author.mention)
    embed.add_field(name="Winners", value=str(winners_count))
    embed.add_field(name="Time Left", value=duration)
    embed.set_footer(text="React with 🎉 to enter!")
    message = await ctx.send(embed=embed)

    # Add the reaction for users to participate
    await message.add_reaction("🎉")

    # Store giveaway details in the database
    conn = sqlite3.connect("giveaways.db")
    c = conn.cursor()
    c.execute('''INSERT INTO giveaways (message_id, channel_id, guild_id, prize, host_id, winners_count, end_time, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(message.id), str(ctx.channel.id), str(ctx.guild.id), prize, str(ctx.author.id),
               winners_count, end_time, 'ongoing'))
    conn.commit()
    conn.close()

# Function to update the giveaway message with the time left
async def update_giveaway_message(giveaway):
    message_id, channel_id, guild_id, prize, winners_count, end_time = (
        giveaway[1], giveaway[2], giveaway[3], giveaway[4], giveaway[6], giveaway[7]
    )

    guild = bot_instance.get_guild(int(guild_id))
    channel = guild.get_channel(int(channel_id))
    message = await channel.fetch_message(int(message_id))

    current_time = int(time.time())
    time_left = end_time - current_time

    if time_left <= 0:
        return "ended"

    # Format the time left
    days, remainder = divmod(time_left, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{days}d {hours}h {minutes}m {seconds}s"

    # Update the embed with the new time left
    embed = message.embeds[0]
    embed.set_field_at(2, name="Time Left", value=time_str)
    await message.edit(embed=embed)

    return "ongoing"

# Task loop to check and update ongoing giveaways every second
@tasks.loop(seconds=1)
async def check_giveaways():
    global bot_instance
    current_time = int(time.time())
    conn = sqlite3.connect("giveaways.db")
    c = conn.cursor()
    c.execute("SELECT * FROM giveaways WHERE status = 'ongoing'")
    giveaways = c.fetchall()

    for giveaway in giveaways:
        print(f"Giveaway data: {giveaway}")  # Debugging line
        try:
            # Update unpacking to handle 10 values and ignore the empty string field
            _, message_id, channel_id, guild_id, prize, host_id, winners_count, end_time, _unused, status = giveaway
        except ValueError as e:
            print(f"Error unpacking giveaway data: {e}")
            continue  # Skip this giveaway if there's an unpacking error

        status = await update_giveaway_message(giveaway)
        if status == "ended":
            guild = bot_instance.get_guild(int(guild_id))
            channel = guild.get_channel(int(channel_id))
            message = await channel.fetch_message(int(message_id))

            users = [user async for user in message.reactions[0].users() if not user.bot]

            if not users:
                await channel.send("No participants, giveaway canceled.")
                c.execute("UPDATE giveaways SET status = 'ended' WHERE message_id = ?", (message_id,))
                conn.commit()
                continue

            winners = random.sample(users, min(len(users), int(winners_count)))
            winners_mentions = ", ".join([winner.mention for winner in winners])
            await channel.send(f"🎉 Congratulations {winners_mentions}! You won the giveaway for **{prize}**!")

            c.execute("UPDATE giveaways SET status = 'ended' WHERE message_id = ?", (message_id,))
            conn.commit()

    conn.close()


# Command to reroll a giveaway
async def reroll_giveaway(ctx, message_id: int):
    conn = sqlite3.connect("giveaways.db")
    c = conn.cursor()
    c.execute("SELECT * FROM giveaways WHERE message_id = ? AND status = 'ended'", (str(message_id),))
    giveaway = c.fetchone()

    if not giveaway:
        await ctx.send("Giveaway not found or not ended.")
        return

    channel_id, prize = giveaway[2], giveaway[4]
    channel = ctx.guild.get_channel(int(channel_id))
    message = await channel.fetch_message(message_id)

    users = [user async for user in message.reactions[0].users() if not user.bot]

    if not users:
        await ctx.send("No participants to reroll.")
        return

    winner = random.choice(users)
    await ctx.send(f"🎉 New winner: {winner.mention} for **{prize}**!")

# Command to cancel a giveaway
async def cancel_giveaway(ctx, message_id: int):
    conn = sqlite3.connect("giveaways.db")
    c = conn.cursor()
    c.execute("DELETE FROM giveaways WHERE message_id = ?", (str(message_id),))
    conn.commit()
    conn.close()
    await ctx.send("Giveaway canceled and removed from the database.")

# Function to start the giveaway checking loop
def start_check_giveaways(bot):
    global bot_instance
    bot_instance = bot
    check_giveaways.start()
