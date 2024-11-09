import discord
import sqlite3
from discord.ext import commands

# Connect to the SQLite database file named 'autoresponds.db'
conn = sqlite3.connect("autoresponds.db")
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS autoresponses (
    keyword TEXT PRIMARY KEY,
    response TEXT
)
""")
conn.commit()

# Command to add a new auto-responder
@commands.command(name="autoresponder")
@commands.has_permissions(administrator=True)
async def add_autoresponder(ctx, keyword: str, response: str):
    try:
        cursor.execute("INSERT OR REPLACE INTO autoresponses (keyword, response) VALUES (?, ?)", (keyword.lower(), response))
        conn.commit()
        await ctx.send(f"Auto-responder added: **{keyword}** → {response}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# Command to remove an existing auto-responder
@commands.command(name="remautoresponder")
@commands.has_permissions(administrator=True)
async def remove_autoresponder(ctx, keyword: str):
    cursor.execute("DELETE FROM autoresponses WHERE keyword = ?", (keyword.lower(),))
    conn.commit()
    await ctx.send(f"Auto-responder removed: **{keyword}**")

# Function to handle auto-responses
async def auto_responder(message):
    if message.author.bot:
        return

    cursor.execute("SELECT keyword, response FROM autoresponses")
    rows = cursor.fetchall()

    for keyword, response in rows:
        if keyword.lower() in message.content.lower():
            await message.channel.send(response)
            break
