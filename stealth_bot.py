import discord
from discord.ext import commands
from discord import app_commands

# --- CONFIG ---
GUILD_ID = 1395298836137902090  # Replace with server ID
ALLOWED_ROLE_ID = 1395300265107914783  # Replace with allowed role ID
REVIEW_CHANNEL_ID = 1395300050627727481  # Replace with channel ID to post reviews

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = False  

bot = commands.Bot(command_prefix="!", intents=intents)

class VouchModal(discord.ui.Modal, title="Submit a Vouch"):

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

        # Add fields
        self.helper_input = discord.ui.TextInput(
            label="Who helped you today?",
            placeholder="Enter the helper's name or tag",
            required=True
        )
        self.legit_input = discord.ui.TextInput(
            label="Is this product legitimate?",
            placeholder="Yes / No",
            required=True
        )
        self.comments_input = discord.ui.TextInput(
            label="Any other comments?",
            style=discord.TextStyle.paragraph,
            placeholder="Additional feedback or context",
            required=False
        )

        self.add_item(self.helper_input)
        self.add_item(self.legit_input)
        self.add_item(self.comments_input)

        # Dropdown is handled separately below

    async def on_submit(self, interaction: discord.Interaction):
        # Store the dropdown response in the view
        stars = interaction.client.star_view.get(interaction.user.id)

        # Create the embed
        embed = discord.Embed(title="⭐ New Vouch Received", color=discord.Color.green())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Who Helped:", value=self.helper_input.value, inline=False)
        embed.add_field(name="Stars:", value=stars or "Not selected", inline=False)
        embed.add_field(name="Legitimate:", value=self.legit_input.value, inline=False)
        embed.add_field(name="Comments:", value=self.comments_input.value or "None", inline=False)

        channel = interaction.client.get_channel(REVIEW_CHANNEL_ID)
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Thanks for your vouch!", ephemeral=True)


class StarDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="⭐", value="⭐"),
            discord.SelectOption(label="⭐ ⭐", value="⭐ ⭐"),
            discord.SelectOption(label="⭐ ⭐ ⭐", value="⭐ ⭐ ⭐"),
            discord.SelectOption(label="⭐ ⭐ ⭐ ⭐", value="⭐ ⭐ ⭐ ⭐"),
            discord.SelectOption(label="⭐ ⭐ ⭐ ⭐ ⭐", value="⭐ ⭐ ⭐ ⭐ ⭐"),
        ]
        super().__init__(placeholder="How many stars out of 5?", options=options)

    async def callback(self, interaction: discord.Interaction):
        interaction.client.star_view[interaction.user.id] = self.values[0]
        modal = VouchModal(interaction)
        await interaction.response.send_modal(modal)


class StarView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(StarDropdown())


@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    bot.star_view = {}  # Stores dropdown selections
    print(f"🟢 Logged in as {bot.user}")


@bot.tree.command(name="vouch", description="Submit a review", guild=discord.Object(id=GUILD_ID))
async def vouch(interaction: discord.Interaction):
    # Check role
    user_roles = [role.id for role in interaction.user.roles]
    if ALLOWED_ROLE_ID not in user_roles:
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    # Show dropdown first
    await interaction.response.send_message("Please select your star rating:", view=StarView(), ephemeral=True)
 
import os
bot.run(os.getenv("DISCORD_TOKEN"))
