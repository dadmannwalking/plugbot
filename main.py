import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import asyncio

# Social media handler imports
import twitter
import bluesky

# Helper imports
import message as msghelper

# Set up environment
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# These should eventually come from the config.json once the project has been updated
# to support multiple servers.
bluesky_username = os.getenv('BLUESKY_USERNAME')
bluesky_password = os.getenv('BLUESKY_PASSWORD')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
# NOTE: May need to activate more and/or disable some as the project needs; see 
# https://discordpy.readthedocs.io/en/stable/intents.html for more information!
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

# Local variables
configuration_role = "admin"
watched_channels = []
permitted_users = []
keywords = []

twitter_config = None
bluesky_config = None
facebook_config = None
reddit_config = None
instagram_config = None

# Load config from config.json file
def load_config():
    global configuration_role
    global watched_channels
    global permitted_users
    global keywords
    global twitter_config
    global bluesky_config
    global facebook_config
    global reddit_config
    global instagram_config

    with open("config.json", "r") as file:
        data = json.load(file)
        configuration_role = data.get("configuration_role", "admin")
        watched_channels = data.get("watched_channels", [])
        permitted_users = data.get("permitted_users", [])
        keywords = data.get("keywords", [])
        twitter_config = data.get("twitter", None)
        bluesky_config = data.get("bluesky", None)
        facebook_config = data.get("facebook", None)
        reddit_config = data.get("reddit", None)
        instagram_config = data.get("instagram", None)

    bluesky.username = bluesky_username
    bluesky.password = bluesky_password

# Update config stored in config.json file
def update_config():
    payload = dict()
    payload["configuration_role"] = configuration_role
    payload["watched_channels"] = watched_channels
    payload["permitted_users"] = permitted_users
    payload["keywords"] = keywords
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
    print("user is not authorized!")
    return False

# Configure bot to watch for prefix commands with given intents
bot = commands.Bot(command_prefix="!pb", intents=intents)

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

# Get and print message history
@bot.command()
async def _gethistory(ctx):
    if authorized(ctx.author) == False:
        return
    
    async for message in ctx.channel.history(limit=10):
        if message.author == bot.user:
            continue
        
        if permitted_users != [] and message.author.name not in permitted_users:
            continue
        
        if message.channel.id not in watched_channels:
            continue

        print("========================================================================")
        print(msghelper.json_from(message))
        
        title, desc, url, thumb, test = msghelper.handle(message=message)
        await bluesky.create_post(title, desc, url, thumb, ctx)
        print("created post!")
        return

# Set up twitter instance
@bot.command()
async def _twitter(ctx):
    if authorized(ctx.author) == False:
        return
    
    await ctx.reply("Twitter integration is currently disabled, sorry!")
    # await ctx.reply(f"Please visit {get_twitter_auth_url()} to authenticate the bot!")

# Test Twtitter instance
@bot.command()
async def _testtwitter(ctx, *, msg):
    if authorized(ctx.author) == False:
        return
    
    await ctx.reply('Twitter not yet integrated...')

# Test bluesky instance
@bot.command()
async def _testbluesky(ctx, *, msg):
    if authorized(ctx.author) == False:
        return
    
    await bluesky.test(ctx, msg)

# Enable and configure Bluesky
@bot.command()
async def _enablebluesky(ctx, *, msg):
    print("TODO: enable and store username and password")

# ================================================================================================ #
# ================================================================================================ #
# =========================================== EVENTS ============================================= #
# ================================================================================================ #
# ================================================================================================ #

@bot.event
async def on_ready():
    print(f"{bot.user.name}, reporting for duty!")

@bot.event
async def on_guild_join(guild):
    print(f"{guild.name} has added plugbot [{guild.id}]")

# Monitor messages sent in channels
@bot.event
async def on_message(message):
    if message.author == bot.user:
        print("don't monitor bot messages")
        return await bot.process_commands(message)
    
    if permitted_users != [] and message.author.name not in permitted_users:
        print(f"only monitor message from permitted users not [{message.author.name}]")
        return await bot.process_commands(message)
    
    if message.channel.id not in watched_channels:
        print("only monitor messages from subbed channels")
        return await bot.process_commands(message)
    
    if bluesky_config.get("enabled", False):
        title, description, url, thumbnail, test = msghelper.handle(message)
        if keywords == []:
            print("posting to Bluesky because keywords are empty...")
            await bluesky.create_post(title, description, url, thumbnail, ctx)
            return await bot.process_commands(message)
        for keyword in keywords:
            if keyword in test:
                print("posting to Bluesky because keyword is present...")
                await bluesky.create_post(title, description, url, thumbnail, ctx)
                return await bot.process_commands(message)

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