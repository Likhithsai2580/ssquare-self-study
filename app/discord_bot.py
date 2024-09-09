import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
GUILD_ID = int(os.environ.get('DISCORD_GUILD_ID'))

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        print(f'{bot.user} is connected to the following guild: {guild.name}(id: {guild.id})')

async def send_message_to_channel(channel_name, message):
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            await channel.send(message)
        else:
            print(f"Channel {channel_name} not found")
    else:
        print("Guild not found")

def run_discord_bot():
    bot.run(TOKEN)

# Run the bot in a separate thread
def start_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_discord_bot())