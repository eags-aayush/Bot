import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

# Define the ticket command
@commands.command(name="ticket")
async def ticket(ctx):
    """
    Creates a button-based ticket system for users to select a ticket type.
    Usage:
    - !ticket -> Sends a message with multiple buttons to create different types of tickets.
    """
    # Create buttons for different ticket categories
    player_report_button = Button(label="Player Report", style=discord.ButtonStyle.blurple)
    support_button = Button(label="Support", style=discord.ButtonStyle.secondary)
    purchase_button = Button(label="Purchase Issue", style=discord.ButtonStyle.red)

    # Define the callback function for each button
    async def player_report_callback(interaction):
        await create_ticket(interaction, "Player Report")

    async def support_callback(interaction):
        await create_ticket(interaction, "Support")

    async def purchase_callback(interaction):
        await create_ticket(interaction, "Purchase Issue")

    # Attach the callbacks to the buttons
    player_report_button.callback = player_report_callback
    support_button.callback = support_callback
    purchase_button.callback = purchase_callback

    # Create a view to hold the buttons
    view = View()
    view.add_item(player_report_button)
    view.add_item(support_button)
    view.add_item(purchase_button)

    # Send a message with the buttons
    await ctx.send("Select the type of ticket you would like to create:", view=view)


# Helper function to create the ticket based on the category
async def create_ticket(interaction, ticket_type):
    user = interaction.user  # The user who clicked the button

    # Check if the user already has an open ticket
    existing_ticket = discord.utils.get(interaction.guild.text_channels, name=f"{user.name}")
    if existing_ticket:
        response_message = await interaction.response.send_message(
            f"{user.mention}, you already have an open ticket: {existing_ticket.mention}", ephemeral=True
        )
        await asyncio.sleep(5)
        await response_message.delete()
        return

    # Define categories based on the ticket type
    category_name = None
    if ticket_type == "Player Report":
        category_name = "Player Reports"
    elif ticket_type == "Support":
        category_name = "Support"
    elif ticket_type == "Purchase Issue":
        category_name = "Purchase Issues"

    # Check if the respective category exists, create it if not
    category = discord.utils.get(interaction.guild.categories, name=category_name)
    if not category:
        category = await interaction.guild.create_category(category_name)

    # Create the ticket channel under the respective category
    channel_name = user.name
    ticket_channel = await interaction.guild.create_text_channel(channel_name, category=category)

    # Set permissions for the channel
    await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)  # Hide from @everyone
    await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)  # Allow user to view and send messages
    staff_role = discord.utils.get(interaction.guild.roles, name="Staff")  # Replace 'Staff' with your staff role name
    if staff_role:
        await ticket_channel.set_permissions(staff_role, read_messages=True, send_messages=True)  # Allow staff to view and send messages

    # Send a confirmation message that will be deleted after 5 seconds
    response_message = await interaction.response.send_message(f"{user.mention}, your {ticket_type} ticket has been created: {ticket_channel.mention}", ephemeral=True)
    await asyncio.sleep(5)
    await response_message.delete()

    # Optionally, send a message in the ticket channel to notify the user
    await ticket_channel.send(f"Hello {user.mention}, your {ticket_type} ticket has been created! Staff will assist you shortly. Till then you can describe your issue!")


# Define the ticket close command
@commands.command(name="ticketclose")
@commands.has_permissions(manage_channels=True)
async def ticket_close(ctx):
    """
    Closes the current ticket channel.
    Usage:
    - !ticketclose -> Closes the ticket channel after a confirmation.
    """
    # Check if the command is used in a ticket channel
    if not ctx.channel.name.startswith(("player-report-", "support-", "purchase-")):
        await ctx.send("This command can only be used in a ticket channel.")
        return

    # Ask for confirmation
    confirmation_message = await ctx.send("Are you sure you want to close this ticket? Type `!confirm` to proceed.")

    def check(m):
        return m.content == "!confirm" and m.author == ctx.author

    try:
        # Wait for user confirmation
        await ctx.bot.wait_for("message", check=check, timeout=30)
        await ctx.send("Closing the ticket...")

        # Delete the ticket channel
        await ctx.channel.delete()
    except asyncio.TimeoutError:
        await ctx.send("Ticket close request timed out. Please try again.")
