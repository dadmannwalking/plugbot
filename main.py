import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import asyncio

from config import get_config, set_config

# Social media handler imports
import twitter
import bluesky

# Helper imports
import message as msghelper

# Set up environment
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
# NOTE: May need to activate more and/or disable some as the project needs; see 
# https://discordpy.readthedocs.io/en/stable/intents.html for more information!
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

# For some reason, commands.has_role() does not like the role being configured via json,
# so this function will determine if a given user has authorization to use a protected
# function
def authorized(user, guild_id: int) -> bool:
    config = get_config(guild_id=guild_id)
    for role in user.roles:
        if role.name == config.configuration_role:
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
    if authorized(ctx.author, ctx.guild.id) == False:
        return
    
    config = get_config(ctx.guild.id)
    watched_channels = config.watched_channels

    try:
        channel_id = int(msg.strip())
        if channel_id in watched_channels:
            await ctx.reply(f"{channel_id} is already monitored")
        else:
            watched_channels.append(channel_id)
            config.watched_channels = watched_channels
            set_config(config, ctx.guild.id)
            await ctx.reply(f"added {channel_id} to monitored channels")
    except ValueError:
        await ctx.reply(f"{msg} is not a valid channel id")

# Remove channel from message monitoring
@bot.command()
async def _unsub(ctx, *, msg):
    if authorized(ctx.author, ctx.guild.id) == False:
        return
    
    config = get_config(ctx.guild.id)
    watched_channels = config.watched_channels

    try:
        channel_id = int(msg.strip())
        if channel_id in watched_channels:
            watched_channels.remove(channel_id)
            config.watched_channels = watched_channels
            set_config(config, ctx.guild.id)
            await ctx.reply(f"removed {channel_id} from monitored channels")
        else:
            await ctx.reply(f"{channel_id} is not currently monitored")
    except ValueError:
        await ctx.reply(f"{msg} is not a valid channel id")

# Get and print message history
@bot.command()
async def _gethistory(ctx):
    if authorized(ctx.author, ctx.guild.id) == False:
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
    if authorized(ctx.author, ctx.guild.id) == False:
        return
    
    await ctx.reply("Twitter integration is currently disabled, sorry!")
    # await ctx.reply(f"Please visit {get_twitter_auth_url()} to authenticate the bot!")

# Test Twtitter instance
@bot.command()
async def _testtwitter(ctx, *, msg):
    if authorized(ctx.author, ctx.guild.id) == False:
        return
    
    await ctx.reply('Twitter not yet integrated...')

# Test bluesky instance
@bot.command()
async def _testbluesky(ctx, *, msg):
    if authorized(ctx.author, ctx.guild.id) == False:
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