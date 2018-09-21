# Slowmode designed by AXVin
# It patches the API to set the slowmode!
# Slowmode is currently an un-released feature but still i got it here!!
# This is the first cog that i have written!!

# Importing all the libraries and red stuff
import asyncio
import discord
from discord.http import Route
from discord.ext import commands
from __main__ import send_cmd_help
from .utils.dataIO import dataIO
from .utils import checks

# Defining the class

class Slowmode:
    """Enable SlowMode in your server"""
    
    def __init__(self, bot):
        self.bot = bot
        
# The main command! Good for showing cmd help help too!

    @commands.group(pass_context=True, no_pm=True)
    async def slowmode(self, ctx):
        """A slowmode to look official"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

# Subcommand to enable the slowmode

    @slowmode.command(name="enable", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _enable(self, ctx, time: int):
        """Enable the slowmode. Time must be in seconds and a value between 0 and 120)"""
        
        if 0 < time <= 120:               # Checks if time is between 0 and 120 as beyond that isn't allowed by Discord
            await self.set_slowmode(ctx, time)
            msg = "Slowmode for this channel set to {} seconds".format(time)
        else:                             # Response for a value which isn't supported
            msg = "Time must be between 0 to 120!"
            
        await self.bot.say(msg)
        
# Subcommand to disable slowmode
       
    @slowmode.command(name="disable", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _disable(self, ctx):
        """Disables the slowmode"""
        
        await self.set_slowmode(ctx, 0)              # Not the official way to disable it though! So simply setting slowmode timing to 0!
        msg = "Removed slowmode from this channel!"
        await self.bot.say(msg)


    async def set_slowmode(self, ctx, time):   # The snippet which actually does the slowmode thing!
        route = Route('PATCH', '/channels/{channel_id}', channel_id=ctx.message.channel.id)       # Defining a variable route which Routes to the channel by method PATCH 
        await self.bot.http.request(route, json={'rate_limit_per_user': time})                    # Actually patching the 'rate_limit_per_user' to enable slowmode!
            
            
def setup(bot):                    # No fun of writing codes if i don't define it as a cog for my bot :aSuperCoolWinkEmoji:
    bot.add_cog(Slowmode(bot))
    
    
    
    
    
    
    
    
    