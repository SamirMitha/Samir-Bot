import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_list = []
        self.help_message = """
```
---General commands---
+help - displays all the available commands

---Music Commands---
+play <keywords> - Finds and plays a song from YouTube
+queue - Displays the current music queue
+skip - Skips the current song being played
+clear - Stops the music and clears the queue
+leave - Disconnects the bot from the voice channel
+pause - Pauses the current song being played or resumes if already paused
+resume - Resumes playing the current song

---Game Commands---
+catan - Sends a Catan link
+codenames - Sends a Codenames link
+monopolydeal - Sends a Monopoly Deal link
+cardsagainsthumanity - Sends a Cards Against Humanity link
```
"""

    # Override bot help prompt
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)

        await self.send_to_all(self.help_message)        

    @commands.command(name="help", help="displays all the available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)
