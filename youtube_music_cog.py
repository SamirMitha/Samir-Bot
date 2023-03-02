from ast import alias
import discord
from discord.ext import commands
import asyncio
import datetime

from youtube_dl import YoutubeDL

class yt_music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc = None
    
        # Music playing semaphores
        self.is_playing = False
        self.is_paused = False
        self.is_finished = False

        # 2D Array Containing: [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    # Search items on YouTube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
                print(info)
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title'], 'playlist_id': info['webpage_url'], 'channel': info['channel'], 'thumbnail': info['thumbnail'], 'uploader_url': info['uploader_url'], 'duration': info['duration']}


    def now_playing(self):
        global embed
        embed = discord.Embed(title=m_title, url=m_playlist_id)
        embed.set_author(name=m_channel, url=m_uploader_url)
        embed.set_thumbnail(url=m_thumbnail)
        embed.add_field(name="Duration", value=str(datetime.timedelta(seconds=m_duration)), inline=True)
        embed.add_field(name="Quality", value="Best", inline=True)
        
        return(embed)


    def update_m(self):
        global m_url
        global m_title
        global m_playlist_id
        global m_channel
        global m_thumbnail
        global m_uploader_url
        global m_duration
        m_url = self.music_queue[0][0]['source']
        m_title = self.music_queue[0][0]['title']
        m_playlist_id = self.music_queue[0][0]['playlist_id']
        m_channel = self.music_queue[0][0]['channel']
        m_thumbnail = self.music_queue[0][0]['thumbnail']
        m_uploader_url = self.music_queue[0][0]['uploader_url']
        m_duration = self.music_queue[0][0]['duration']


    def play_next(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            self.update_m()
            embed = self.now_playing()

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            asyncio.run_coroutine_threadsafe(ctx.send("Now Playing: **{}**".format(m_title), embed=embed), self.bot.loop)
        else:
            self.is_playing = False


    # Infinite Loop Checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Update global variables and create embed to send when playing
            self.update_m()
            embed = self.now_playing()
            
            # If not in voice channel, try to connect
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                await ctx.guild.change_voice_state(channel=self.music_queue[0][1], self_mute=False, self_deaf=True)

                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel.")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
                await ctx.guild.change_voice_state(channel=self.music_queue[0][1], self_mute=False, self_deaf=True)
            
            # Pop music queue when playing
            self.music_queue.pop(0)
            
            # Send embed when playing
            await ctx.send("Now Playing: **{}**".format(m_title), embed=embed)
            #self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS))
            
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda x: self.play_next(ctx))
                
        else:
            self.is_playing = False


    # Bot Commands
    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("You are not in a voice channel.")
            return

        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format or something. This could be due to playlist or a livestream format, I haven't really figured it out yet.")
            else:
                if self.is_playing == True:
                    await ctx.send("**{}** added to queue in position **{}**".format(song['title'], len(self.music_queue) + 1))
                    self.music_queue.append([song, voice_channel])
                else:
                    self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music(ctx)


    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()


    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()


    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            if len(self.music_queue) > 0:
                await ctx.send("Skipping: **{}**".format(m_title))
                self.vc.stop()

            else:
                self.vc.stop()
                await ctx.send("There is no music in the queue. The bot will disconnect after 10 minutes of inactivity.")


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += "**{}** - **{}**\n".format(str(i+1), self.music_queue[i][0]['title'])

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("There is no music in the queue.")


    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Segmentation fault (core dumped)")


    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
        await ctx.send("I left the voice channel.")
        
    # Make Bot leave voice channel after 10 minutes of inactivity
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 600:
                    await voice.disconnect()
                if not voice.is_connected():
                    break
