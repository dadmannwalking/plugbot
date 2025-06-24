import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json

import twitter
import bluesky

# Set up environment
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
# NOTE: May need to activate more and/or disable some as the project needs; see 
# https://discordpy.readthedocs.io/en/stable/intents.html for more information!
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Local variables
prefix = "!pb"
configuration_role = "admin"
watched_channels = []

twitter_config = None
bluesky_config = None
facebook_config = None
reddit_config = None
instagram_config = None

# Load config from config.json file
def load_config():
    global prefix
    global configuration_role
    global watched_channels
    global twitter_config
    global bluesky_config
    global facebook_config
    global reddit_config
    global instagram_config

    with open("config.json", "r") as file:
        data = json.load(file)
        prefix = data.get("prefix", "!pb")
        configuration_role = data.get("configuration_role", "admin")
        watched_channels = data.get("watched_channels", [])
        twitter_config = data.get("twitter", None)
        bluesky_config = data.get("bluesky", None)
        facebook_config = data.get("facebook", None)
        reddit_config = data.get("reddit", None)
        instagram_config = data.get("instagram", None)

def update_config():
    payload = dict()
    payload["prefix"] = prefix
    payload["configuration_role"] = configuration_role
    payload["watched_channels"] = watched_channels
    payload["twitter"] = twitter_config
    payload["bluesky"] = bluesky_config
    payload["facebook"] = facebook_config
    payload["reddit"] = reddit_config
    payload["instagram"] = instagram_config
    
    with open("config.json", "w") as file: 
        json.dump(payload, file, indent=4)

# For some reason, commands.has_role() does not like the role being configured via json,
# so this function will determine if a given user has authorization to use a protected
# function
def authorized(user):
    for role in user.roles:
        if role.name == configuration_role:
            return True
    return False

# Set up bot to listen for prefix commands
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name}, reporting for duty!")

# ================================================================================================ #
# ================================================================================================ #
# ====================================== PREFIX COMMANDS ========================================= #
# ================================================================================================ #
# ================================================================================================ #

# Register channel for message monitoring
@bot.command()
async def _sub(ctx, *, msg):
    if authorized(ctx.author) == False:
        print("user is not authorized")
        return
    
    try:
        channel_id = int(msg)
        if channel_id in watched_channels:
            await ctx.reply(f"{channel_id} is already monitored {watched_channels}")
        else:
            watched_channels.append(channel_id)
            update_config()
            await ctx.reply(f"added {channel_id} to monitored channels {watched_channels}")
    except ValueError:
        await ctx.reply(f"{msg} is not a valid channel id")

# Remove channel from message monitoring
@bot.command()
async def _unsub(ctx, *, msg):
    if authorized(ctx.author) == False:
        print("user is not authorized")
        return

    try:
        channel_id = int(msg)
        if channel_id in watched_channels:
            watched_channels.remove(channel_id)
            update_config()
            await ctx.reply(f"removed {channel_id} from monitored channels {watched_channels}")
        else:
            await ctx.reply(f"{channel_id} not in watched channels...")
    except ValueError:
        await ctx.reply(f"{msg} is not a valid channel id")

# Set up twitter instance
@bot.command()
async def _twitter(ctx):
    await ctx.reply("Twitter integration is currently disabled, sorry!")
    # await ctx.reply(f"Please visit {get_twitter_auth_url()} to authenticate the bot!")

# Set up bluesky instance
@bot.command()
async def _blueskytest(ctx, *, msg):
    print(1)
    await bluesky.test(ctx, msg)
    print(2)

# ================================================================================================ #
# ================================================================================================ #
# ========================================== SWIZZLES ============================================ #
# ================================================================================================ #
# ================================================================================================ #

# Monitor messages sent in channels
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Watch for updates that should be posted to social media
    for channel in watched_channels:
        try:
            channel_id = int(channel)
            if message.channel.id == channel_id:
                print(f"should send {message} to social media")
        except ValueError:
            print("")

    # NOTE: always required, this function is effectively an override allows continued
    # handling of other messages
    await bot.process_commands(message)

# ================================================================================================ #
# ================================================================================================ #
# ========================================== BOT SETUP =========================================== #
# ================================================================================================ #
# ================================================================================================ #

# Configure and run the bot
load_config()
bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)