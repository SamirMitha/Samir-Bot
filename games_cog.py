from ast import alias
import discord
from discord.ext import commands

from utils import id_generator

class games_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    # Bot Commands
    @commands.command(name="catan", help="Sends a Catan link")
    async def catan(self, ctx):
        await ctx.send('https://colonist.io/#' + id_generator())
    
    @commands.command(name="codenames", help="Sends a Codenames link")
    async def codenames(self, ctx):
        await ctx.send('https://www.horsepaste.com/' + id_generator())
        
    @commands.command(name="monopolydeal", help="Sends a Monopoly Deal link")
    async def monopolydeal(self, ctx):
        await ctx.send('https://www.covidopoly.io')
        
    @commands.command(name="cardsagainsthumanity", help="Sends a Cards Against Humanity link")
    async def cardsagainsthumanity(self, ctx):
        await ctx.send('https://cardsagainstformality.io/')
