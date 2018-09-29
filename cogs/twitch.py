
# importing the libraries
import os
import requests
import discord
import asyncio
import aiohttp
from discord.ext import commands
from __main__ import send_cmd_help
from .utils.dataIO import dataIO
from .utils import checks


class Twitch:
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/twitch/system.json"
        self.system = dataIO.load_json(self.file_path)



    @commands.group(pass_context=True, no_pm=True)
    async def twitch(self, ctx):
        """
        Some simple twitch tools! Made by AXVin.
        """
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)




    @twitch.command(name="followers", pass_context=True, no_pm=True)
    async def _followers(self, ctx, streamer=None):
        """
        Get the total followers of the streamer! By default, the default streamer is used!!
        """
        user = ctx.message.author
        settings = self.check_server_settings(user.server)
        default_streamer = settings["Config"]["Default Streamer"]
        if streamer == None:
            if default_streamer != None:
                streamer = default_streamer
            else:
                await self.bot.say("Please either provide the login name of the streamer Or set the default streamer by using `{}twitchset defaultstreamer` command".format(ctx.prefix))
                return
            
        streamer_check = await self.streamer_check(settings, streamer)
        
        if streamer_check == True:
            client_id_check = await self.check_for_client_id(settings)
            if client_id_check == True:
                client_id = settings["Config"]["Client-ID"]
                url = 'https://api.twitch.tv/helix/users/follows'
                streamer_id = settings["Streamers"][streamer]["Streamer ID"]
                parameters = {'to_id' : streamer_id}
                headers = {'Client-ID' : client_id}
        
                jsondata = await self.get_data(url, parameters, headers)
        
                display_name = settings["Streamers"][streamer]["Display Name"]
                followers = jsondata["total"]     # Now we have total followers in followers variable
                msg = "**{}** has {} followers".format(display_name, followers)
                await self.bot.say(msg)




    @twitch.command(name="views", pass_context=True, no_pm=True)
    async def _views(self, ctx, streamer=None):
        """
        Get the total views of the streamer! By default, the default streamer is used!!
        """
        user = ctx.message.author
        settings = self.check_server_settings(user.server)
        default_streamer = settings["Config"]["Default Streamer"]
        if streamer == None:
            if default_streamer != None:
                streamer = default_streamer
            else:
                await self.bot.say("Please either provide the login name of the streamer Or set the default streamer by using `{}twitchset defaultstreamer` command".format(ctx.prefix))
                return
            
        streamer_check = await self.streamer_check(settings, streamer)
        
 #       streamer_id = settings["Streamers"][streamer]["Streamer ID"]
        if streamer_check == True:
            url = 'https://api.twitch.tv/helix/users'
            parameters = {'login' : streamer}
            
            client_id_check = await self.check_for_client_id(settings)
            if client_id_check == True:
                client_id = settings["Config"]["Client-ID"]
                headers = {'Client-ID' : client_id}
        
                jsondata = await self.get_data(url, parameters, headers)
        
                display_name = settings["Streamers"][streamer]["Display Name"]
                views = jsondata["data"][0]["view_count"]     # Now we have total followers in followers variable
                msg = "**{}** has {} views".format(display_name, views)
                await self.bot.say(msg)









    @commands.group(pass_context=True, no_pm=True)
    async def twitchset(self, ctx):
        """
        The commands for setting the information about twitch cog!
        """
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)


    @twitchset.command(name="defaultstreamer", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _default_streamer(self, ctx, streamer):
        """Sets the default streamer of the server!"""
        user = ctx.message.author
        settings = self.check_server_settings(user.server)
        streamer_check = await self.streamer_check(settings, streamer)
        if streamer_check == True:
            settings["Config"]["Default Streamer"] = streamer
            dataIO.save_json(self.file_path, self.system)
            await self.bot.say("Made {} as the default streamer for this server".format(streamer))



    @twitchset.command(name="client-id", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _set_client_id(self, ctx, client_id):
        """
        Sets the client id required for requesting information.
        Without it this bot is useless!
        To do this, follow these steps:
          1. Go to this page: https://dev.twitch.tv/dashboard/apps.
          2. Click 'Register Your Application'
          3. Enter a name, set the OAuth Redirect URI to 'http://localhost', and
             select an Application Category of your choosing.
          4. Click 'Register', and on the following page, copy the Client ID.
          5. Paste the Client ID into this command. Done!
        """
        # DELETE THE MESSAGE INVOKING THE COMMAND
        message = ctx.message
        await self.bot.delete_message(message)
        user = ctx.message.author
        
        try:
            url = 'https://api.twitch.tv/helix/users/follows'
            parameters = {'to_id' : '47514919'}
            headers = {'Client-ID' : client_id}
            await self.get_data(url, parameters, headers)
            pass
        except:
            await self.bot.say("Invalid Client-ID! Please try again.")
            return
            
        settings = self.check_server_settings(user.server)
        settings["Config"]["Client-ID"] = client_id
        dataIO.save_json(self.file_path, self.system)
        await self.bot.say("Client-ID set successfully!")



    @twitchset.command(name="addstreamer", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _add_streamer(self, ctx, streamer):
        """Adds a  streamer to the server list!"""
        user = ctx.message.author
        settings = self.check_server_settings(user.server)
        streamer_check = await self.streamer_check(settings, streamer)
        if streamer_check == True:
            await self.bot.say('Successfully added {} to the list of streamers!'.format(streamer))





    @twitchset.command(name="config-followercount", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _config_follower_count(self, ctx):
        """
        Sets the channel to show followercount!!
        The fun part is that you need not to work with the hassle of getting voice channel ids!
        Just create a voice channel(name it anything), join that channel and run this command!!
        Awesome, right?
        You must set the default streamer in order to run this command!!
        """
        user = ctx.message.author
        server = ctx.message.server
        voice_channel = user.voice_channel
        settings = self.check_server_settings(user.server)
        
        if voice_channel is not None:
            default_streamer = settings["Config"]["Default Streamer"]
            
            if default_streamer != None:
                streamer = default_streamer
            else:
                await self.bot.say("Please set the default streamer by using `{}twitchset defaultstreamer` command".format(ctx.prefix))
                return
            
            settings["Config"]["VC Channel"] = voice_channel.id
            await self.bot.say('Do you want to enable it right now?')
            enable = await self.bot.wait_for_message(timeout=35, author=user)

            if enable is None:
                await self.bot.say('You took too long to respond! You can enable it later by using the `{}twitchset enablefollowercount` command.'.format(ctx.prefix))
            elif enable.content == 'Yes' or enable.content == 'yes':
                settings["Config"]["VC Display"] = True
                await self.bot.say("Enabled the followercount in this server!")
            else:
                self.bot.say('Okay, I disabled the followetcount for this server. You can enable it later by using the `{}twitchset enablefollowercount` command.'.format(ctx.prefix))
            
            dataIO.save_json(self.file_path, self.system)
        else:
            await self.bot.say('Please join a voice channel in which you want to show the follower count')




    @twitchset.command(name="followercount", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _enable_or_disable_follower_count(self, ctx, decision):
        """
        The command used to enable or disable followercount.
        Please run [p]twitchset config-followercount before running the command.
        Decision must be either enable or disable.
        """
        user = ctx.message.author
        server = ctx.message.server
        settings = self.check_server_settings(user.server)
        vc_channel = settings["Config"]["VC Channel"]
        vc_display = settings["Config"]["VC Display"]
        if vc_channel == None:
            await self.bot.say("It seems like you didn't run the `{}twitchset config-followercount` command! Please run it in order to use this command!".format(ctx.prefix))
            return
        else:
            if decision == 'enable':
                if vc_display != True:
                    vc_display = True
                    dataIO.save_json(self.file_path, self.system)
                    await self.bot.say('Enabled FollowerCount in this server!')
                else:
                    await self.bot.say('FollowerCount is already enabled for this server!')
                    return
            elif decision == 'disable':
                if vc_display != False:
                    vc_display = False
                    dataIO.save_json(self.file_path, self.system)
                    await self.bot.say('Disable FollowerCount in this server!')
                else:
                    await self.bot.say('FollowerCount is already disabled for this server!')
                    return
            else:
                await self.bot.say('Please either choose enable or disable!')
                return



    async def follower_check(self):
        check_delay = 15
        servers = self.system["Servers"]
        while self == self.bot.get_cog('Twitch'):
            for server in servers:
                config = servers[server]["Config"]
                if config["VC Display"] == True:
                    vc_channel_id = config["VC Channel"]
                    vc_channel = self.bot.get_channel(vc_channel_id)
                    streamer = config["Default Streamer"]
                    server_ob = self.bot.get_server(server)
                    if server_ob != None:
                        settings = self.check_server_settings(server_ob)

                        client_id_check = await self.check_for_client_id(settings)
                        if client_id_check == True:
                            client_id = settings["Config"]["Client-ID"]
                            url = 'https://api.twitch.tv/helix/users/follows'
                            streamer_id = settings["Streamers"][streamer]["Streamer ID"]
                            parameters = {'to_id' : streamer_id}
                            headers = {'Client-ID' : client_id}
        
                            jsondata = await self.get_data(url, parameters, headers)
        
                            display_name = settings["Streamers"][streamer]["Display Name"]
                            follower = jsondata["total"]
                        
                            name = 'Followers: {}'.format(follower)
                            await self.bot.edit_channel(vc_channel, name=name)
            
            await asyncio.sleep(check_delay)









    async def check_for_client_id(self, settings):
        client_id = settings["Config"]["Client-ID"]
        if client_id == None:
            await self.bot.say("You don't have a Client-ID set. Set it by using `twitchset client-id` command!")
            return False
        else:
            return True




    async def get_data(self, url, parameters, headers):
#        NOT USING REQUESTS ANYMORE
        r = requests.get(url, params=parameters, headers=headers)
        return r.json()
        
#        LONG LIVE AIOHTTP!!
   #     async with aiohttp.ClientSession() as session:
   #         async with session.get(url, params=parameters, headers=headers) as resp:
   #             return resp.json()


    async def streamer_check(self, settings, streamer):
        if streamer in settings["Streamers"]:
            return True
        else:
                   # try to get id from streamer's name!!
            
            url = 'https://api.twitch.tv/helix/users'
            parameters = {'login' : streamer}
            client_id_check = await self.check_for_client_id(settings)
            if client_id_check == True:
                client_id = settings["Config"]["Client-ID"]
                headers = {'Client-ID' : client_id}
                try:
                    jsondata = await self.get_data(url, parameters, headers)
                    streamer_id = jsondata["data"][0]["id"]          # try to get id in streamer_id variable!
                    display_name = jsondata["data"][0]["display_name"]
                #GET DISPLAY NAME ASAP!!
                    settings["Streamers"][streamer] = {"Streamer ID": streamer_id,
                                                       "Display Name" : display_name}
                    
                    if settings["Config"]["Default Streamer"] == None:
                        settings["Config"]["Default Streamer"] = streamer
                        print('Made {} as the default streamer'.format(display_name))
                    dataIO.save_json(self.file_path, self.system)
                    print("Added {} to twitch cog's data!\nDisplay Name: {}\nID: {}".format(streamer, display_name, streamer_id))
                
                    return True
                except Exception as e:
                    await self.bot.say('Streamer Not found! Please give the exact login username of the streamer. It is the lowercase of Display Name usually\n Error: {}'.format(e))
                
                    return False



    def check_server_settings(self, server):
        if server.id not in self.system["Servers"]:
            self.system["Servers"][server.id] = {"Streamers": {},
                                                 "Config": {"Default Streamer": None,
                                                            "Client-ID": None,
                                                            "VC Category": None,
                                                            "VC Channel": None,
                                                            "VC Display": False}
                                                 }
            dataIO.save_json(self.file_path, self.system)
            print("Creating default twitch settings for Server: {}".format(server.name))
            path = self.system["Servers"][server.id]
            return path
        else:
            path = self.system["Servers"][server.id]
            return path



def check_folders():
    if not os.path.exists("data/twitch"):   # Checks for parent directory for all Jumper cogs
        print("Creating the default folder named twitch...")
        os.makedirs("data/twitch")


def check_files():
    default = {"Servers": {},
               "Version": "1.0.0"
               }

    f = "data/twitch/system.json"
    if not dataIO.is_valid_json(f):
        print("Creating default twitch system.json...")
        dataIO.save_json(f, default)
    else:
        current = dataIO.load_json(f)
        if current["Version"] != default["Version"]:
            print("Updating Twitch Cog from version {} to version {}".format(current["Version"],
                                                                           default["Version"]))
            current["Version"] = default["Version"]
            dataIO.save_json(f, current)


def setup(bot):
    check_folders()
    check_files()
    n = Twitch(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.follower_check())
    bot.add_cog(n)





