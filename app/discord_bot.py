import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Discord configuration with defaults
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD_ID = os.environ.get('DISCORD_GUILD_ID', '0')  # Default to '0' if not set
CHANNEL_ID = os.environ.get('DISCORD_CHANNEL_ID', '0')  # Default to '0' if not set

# Convert to integers with error handling
try:
    GUILD_ID = int(GUILD_ID)
    CHANNEL_ID = int(CHANNEL_ID)
except ValueError:
    print("Warning: Invalid Discord Guild ID or Channel ID")
    GUILD_ID = 0
    CHANNEL_ID = 0

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    if GUILD_ID:
        guild = discord.utils.get(bot.guilds, id=GUILD_ID)
        if guild:
            print(f'{bot.user} is connected to the following guild: {guild.name}(id: {guild.id})')

async def send_message_to_channel(channel_name, message):
    if GUILD_ID:
        guild = discord.utils.get(bot.guilds, id=GUILD_ID)
        if guild:
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                await channel.send(message)
            else:
                print(f"Channel {channel_name} not found")
        else:
            print("Guild not found")
    else:
        print("Discord integration is not configured")

def run_discord_bot():
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Discord bot token not found. Discord integration is disabled.")

# Run the bot in a separate thread
def start_discord_bot():
    if TOKEN:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_discord_bot())
    else:
        print("Discord integration is disabled.")