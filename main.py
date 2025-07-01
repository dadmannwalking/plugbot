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

def taglog(msg):
    print(f"[MAIN] {msg}")

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

# Configure bot to watch for prefix commands with given intents
bot = commands.Bot(command_prefix='!pb_', intents=intents)

# ================================================================================================ #
# ================================================================================================ #
# ====================================== PREFIX COMMANDS ========================================= #
# ================================================================================================ #
# ================================================================================================ #

# Test basic plugbot integration
@bot.command()
async def test(ctx):
    config = get_config(ctx.guild.id)
    if config.authorized(ctx.author, ctx.guild) == False:
        return

    await ctx.reply("hello there")

# Change admin role for current guild
@bot.command()
async def role(ctx, *, msg):
    config = get_config(ctx.guild.id)
    if config.authorized(ctx.author, ctx.guild) == False:
        return

    for role in ctx.guild.roles:
        if role.name == msg:
            config.configuration_role = msg
            set_config(config, ctx.guild.id)
            return await ctx.reply(f'admin role has been changed to {msg}')

    await ctx.reply(f"{msg} role not found")

# List, add, or remove channels from monitored channels
@bot.command()
async def channels(ctx, *, msg):
    config = get_config(ctx.guild.id)
    if config.authorized(ctx.author, ctx.guild) == False:
        return

    components = msg.split()

    if len(components) == 1 and components[0] == "list":
        if config.watched_channels:
            channels_list = "\n".join(f"`{cid}`" for cid in config.watched_channels)
            await ctx.reply(f"Currently monitored channels:\n{channels_list}")
        else:
            await ctx.reply("No channels are currently being monitored.")
        return

    if len(components) == 2 and components[0] in ["add", "remove"]:
        try:
            channel_id = int(components[1])
            guild_channel_ids = [channel.id for channel in ctx.guild.channels]

            if channel_id not in guild_channel_ids:
                return await ctx.reply(f"`{channel_id}` is not a valid channel id in this guild")

            if components[0] == "add":
                if channel_id in config.watched_channels:
                    return await ctx.reply(f"Channel `{channel_id}` is already being monitored.")
                config.watched_channels.append(channel_id)
                set_config(config, ctx.guild.id)
                return await ctx.reply(f"Channel `{channel_id}` added to monitored channels.")
            
            if components[0] == "remove":
                if channel_id not in config.watched_channels:
                    return await ctx.reply(f"Channel `{channel_id}` is not currently monitored.")
                config.watched_channels.remove(channel_id)
                set_config(config, ctx.guild.id)
                return await ctx.reply(f"Channel `{channel_id}` removed from monitored channels.")
        except Exception as e:
            taglog(f"Exception in channels command: {e}")
            await ctx.reply(f"Invalid channel ID: `{components[1]}`")
        return

    await ctx.reply(f"unable to parse command parameters: `{msg}`")

# List, add, or remove keyword phrases from the list
@bot.command()
async def keywords(ctx, *, msg):
    config = get_config(ctx.guild.id)
    if config.authorized(ctx.author, ctx.guild) == False:
        return

    components = msg.split(maxsplit=1)
    action = components[0]

    if action == "list":
        if config.keywords:
            keywords_list = "\n".join(f"`{kw}`" for kw in config.keywords)
            return await ctx.reply(f"Currently filtering for these phrases:\n{keywords_list}")
        else:
            await ctx.reply("No key phrase filters are currently applied.")
        return

    if len(components) == 2 and action in ["add", "remove"]:
        phrase = components[1].strip().lower()

        if action == "add":
            if phrase in config.keywords:
                return await ctx.reply(f"Key phrase `{phrase}` already exists.")

            config.keywords.append(phrase)
            set_config(config, ctx.guild.id)
            return await ctx.reply(f"Key phrase `{phrase}` added.")

        if action == "remove":
            if phrase not in config.keywords:
                return await ctx.reply(f"Key phrase `{phrase}` does not exist.")

            config.keywords.remove(phrase)
            set_config(config, ctx.guild.id)
            return await ctx.reply(f"Key phrase `{phrase}` removed.")

    await ctx.reply(f"unable to parse command parameters: `{msg}`")

# Get and print message history
@bot.command()
async def gethistory(ctx):
    config = get_config(ctx.guild.id)

    if config.authorized(ctx.author, ctx.guild) == False:
        return
    
    async for message in ctx.channel.history(limit=10):
        if config.confirm(message) == False:
            continue
            
        print("========================================================================")
        print(msghelper.json_from(message))
        
        # title, desc, url, thumb, test = msghelper.handle(message=message)
        # await bluesky.create_post(title, desc, url, thumb, ctx, config)
        # print("created post!")
        # return # Only do the first one to prevent spamming

# Set up twitter instance
@bot.command()
async def twitter(ctx):
    config = get_config(ctx.guild.id)

    if config.authorized(ctx.author, ctx.guild) == False:
        return
    
    await ctx.reply("Twitter integration is currently disabled, sorry!")
    # await ctx.reply(f"Please visit {get_twitter_auth_url()} to authenticate the bot!")

# Test Twtitter instance
@bot.command()
async def testtwitter(ctx, *, msg):
    config = get_config(ctx.guild.id)

    if config.authorized(ctx.author, ctx.guild) == False:
        return
    
    await ctx.reply('Twitter not yet integrated...')

# Test bluesky instance
@bot.command()
async def testbluesky(ctx, *, msg):
    config = get_config(ctx.guild.id)

    if config.authorized(ctx.author, ctx.guild) == False:
        return
    
    await bluesky.test(ctx, msg, config.bluesky)

# Enable and configure Bluesky
@bot.command()
async def enablebluesky(ctx, *, msg):
    # The user should call this with two parameters, divided by a space
    # The first parameter is the bot's username and the second is the password
    config = get_config(ctx.guild.id)
    if config.authorized(ctx.author, ctx.guild) == False:
        return
    
    components = msg.split()
    if len(components) != 2:
        await ctx.reply("This command requires username and password as parameters")
        await ctx.message.delete()
        return

    if config.bluesky is None:
        config.bluesky = ServiceConfig(enable=False)
    
    username = components[0]
    password = components[1]
    config.bluesky.enable(username, password)
    set_config(config, ctx.guild.id)

    await ctx.reply("Bluesky integration enabled successfully.")
    await ctx.message.delete()

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
    config = get_config(message.guild.id)

    if config.confirm(message) == False:
        taglog(f'user not authorized, process {message.content}')
        await bot.process_commands(message)
        return
    
    if config.bluesky.enabled:
        title, description, url, thumbnail, test = msghelper.handle(message)
        if keywords == []:
            print("posting to Bluesky because keywords are empty...")
            await bluesky.create_post(title, description, url, thumbnail, ctx, config.bluesky)
        elif any(keyword in test for keyword in config.keywords):
            print("posting to Bluesky because keyword is present...")
            await bluesky.create_post(title, description, url, thumbnail, ctx, config.bluesky)

    # NOTE: always required, this function is effectively an override allows continued
    # handling of other messages
    taglog(f'fallthrough, process {message.content}')
    await bot.process_commands(message)

# ================================================================================================ #
# ================================================================================================ #
# ========================================== BOT SETUP =========================================== #
# ================================================================================================ #
# ================================================================================================ #

# Configure and run the bot
bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)