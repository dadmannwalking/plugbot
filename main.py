import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import base64
import hashlib
import urllib.parse

# Set up environment
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
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

twitter = None
bluesky = None
facebook = None
reddit = None
instagram = None

# Load config from config.json file
def load_config():
    global prefix
    global configuration_role
    global watched_channels
    global twitter
    global bluesky
    global facebook
    global reddit
    global instagram

    with open("config.json", "r") as file:
        data = json.load(file)
        prefix = data.get("prefix", "!pb")
        configuration_role = data.get("configuration_role", "admin")
        watched_channels = data.get("watched_channels", [])
        twitter = data.get("twitter", None)
        bluesky = data.get("bluesky", None)
        facebook = data.get("facebook", None)
        reddit = data.get("reddit", None)
        instagram = data.get("instagram", None)

def update_config():
    payload = dict()
    payload["prefix"] = prefix
    payload["configuration_role"] = configuration_role
    payload["watched_channels"] = watched_channels
    payload["twitter"] = twitter
    payload["bluesky"] = bluesky
    payload["facebook"] = facebook
    payload["reddit"] = reddit
    payload["instagram"] = instagram
    
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
# ========================================== TWITTER ============================================= #
# ================================================================================================ #
# ================================================================================================ #

def get_twitter_auth_url():
    random_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
    hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).decode('ascii').rstrip('=')

    base_url = "https://twitter.com/i/oauth2/authorize"
    scope = "tweet.write"
    params = {
        "response_type": "code",
        "client_id": twitter_client_id,
        "redirect_uri": twitter.get("redirect_uri",""),
        "scope": scope,
        "state": "random_string",  # TODO: make this a real CSRF-safe random string
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    # Why does ChatGPT suggest returning the code_verifier here??
    # full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    # return full_url, code_verifier
    return f"{base_url}?{urllib.parse.urlencode(params)}"

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