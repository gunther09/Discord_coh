import os
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import firebase.firebase_config  # Importiere Firebase-Konfiguration
import game_stats  # Importiere game_stats für die /stats Befehle

# Load environment variables from .env file
load_dotenv()

# Discord Bot Token from environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
# Channel ID where the bot will post
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
# Guild ID where the bot will operate
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))

# Create the bot with command prefix
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Slash Command /players
@bot.slash_command(name="players", description="Manage players", guild_ids=[GUILD_ID])
async def players(interaction: Interaction):
    pass

# Subcommand /players list
@players.subcommand(name="list", description="List all players")
async def players_list(interaction: Interaction):
    db = firebase.firebase_config.db
    players_ref = db.collection('players')
    docs = players_ref.stream()
    
    players = [f"{doc.to_dict().get('alias')} (Relic ID: {doc.to_dict().get('relic_id')})" for doc in docs]
    
    if players:
        players_list_message = "\n".join(players)
        await interaction.response.send_message(f"Players List:\n{players_list_message}")
    else:
        await interaction.response.send_message("No players found.")

# Subcommand /players add
@players.subcommand(name="add", description="Add a new player")
async def players_add(
    interaction: Interaction,
    relic_id: int = SlashOption(description="The relic ID of the player"),
    alias: str = SlashOption(description="The alias of the player")
):
    db = firebase.firebase_config.db
    player_data = {
        'alias': alias,
        'relic_id': relic_id
    }
    
    try:
        db.collection('players').add(player_data)
        await interaction.response.send_message(f"Player {alias} with Relic ID {relic_id} added successfully.")
    except Exception as e:
        await interaction.response.send_message(f"Error adding player: {e}")

# Subcommand /players delete
@players.subcommand(name="delete", description="Delete a player")
async def players_delete(
    interaction: Interaction,
    relic_id: int = SlashOption(description="The relic ID of the player to delete")
):
    db = firebase.firebase_config.db
    
    try:
        players_ref = db.collection('players')
        docs = players_ref.where('relic_id', '==', relic_id).stream()
        
        deleted = False
        for doc in docs:
            doc.reference.delete()
            deleted = True
        
        if deleted:
            await interaction.response.send_message(f"Player with Relic ID {relic_id} deleted successfully.")
        else:
            await interaction.response.send_message(f"No player found with Relic ID {relic_id}.")
    except Exception as e:
        await interaction.response.send_message(f"Error deleting player: {e}")

# Subcommand /players update
@players.subcommand(name="update", description="Update an existing player")
async def players_update(
    interaction: Interaction,
    relic_id: int = SlashOption(description="The relic ID of the player"),
    alias: str = SlashOption(description="The new alias of the player")
):
    db = firebase.firebase_config.db
    
    try:
        players_ref = db.collection('players')
        docs = players_ref.where('relic_id', '==', relic_id).stream()
        
        updated = False
        for doc in docs:
            doc.reference.update({'alias': alias})
            updated = True
        
        if updated:
            await interaction.response.send_message(f"Player with Relic ID {relic_id} updated to alias {alias} successfully.")
        else:
            await interaction.response.send_message(f"No player found with Relic ID {relic_id}. Adding new player.")
            player_data = {
                'alias': alias,
                'relic_id': relic_id
            }
            db.collection('players').add(player_data)
            await interaction.response.send_message(f"Player {alias} with Relic ID {relic_id} added successfully.")
    except Exception as e:
        await interaction.response.send_message(f"Error updating player: {e}")

# Import game_stats to register /stats commands
game_stats.register_stats_commands(bot, GUILD_ID)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print("Bot has successfully started and is ready to receive commands.")

def run_bot():
    # Run the bot
    bot.run(TOKEN)
