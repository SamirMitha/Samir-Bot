import discord
import os
from discord.ext.commands import Bot

from help_cog import help_cog
from youtube_music_cog import yt_music_cog
from games_cog import games_cog

# Clients
intents = discord.Intents.default()
intents.message_content = True
command_prefix = '+'
bot = Bot(intents=intents, command_prefix = command_prefix)
    
# Remove default help command
bot.remove_command('help')

# Initialize bot
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Game(name="Samir Bot | +help"))
    # Load cogs
    await bot.add_cog(help_cog(bot))
    print('[STARTUP] help_cog loaded')
    await bot.add_cog(yt_music_cog(bot))
    print('[STARTUP] yt_music_cog loaded')
    await bot.add_cog(games_cog(bot))
    print('[STARTUP] games_cog loaded')

# Run Bot
bot.run(os.getenv("BOT_TOKEN"))
