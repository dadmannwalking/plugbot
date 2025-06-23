import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json

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
bot_name = "plugbot"
watch_channels = []

twitter = None
bluesky = None
facebook = None
reddit = None
instagram = None

# Load config from config.json file
def load_config():
    with open("config.json", "r") as file:
        global bot_name
        global prefix
        global watch_channels
        global twitter
        global bluesky
        global facebook
        global reddit
        global instagram

        data = json.load(file)

        if data["name"] and data["name"] != "":
            bot_name = data["name"]

        if data["prefix"] and data["prefix"] != "":
            prefix = data["prefix"]

        if data["watch_channels"] and data["watch_channels"] != []:
            watch_channels = data["watch_channels"]
            
        if data["twitter"]:
            twitter = data["twitter"]
            
        if data["bluesky"]:
            bluesky = data["bluesky"]
            
        if data["facebook"]:
            facebook = data["facebook"]
            
        if data["reddit"]:
            reddit = data["reddit"]
            
        if data["instagram"]:
            instagram = data["instagram"]

# Set up bot to listen for prefix commands
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name}, reporting for duty!")

# @bot.event
# async def on_member_join(member):
#     # Will send as a DM; how to send as a reply??
#     await member.send(f"Welcome to the server {member.name}")

# Register channel for message monitoring
@bot.command()
async def _sub(ctx, *, msg):
    watch_channels.append(msg)
    await ctx.reply(f"{msg} has been added to monitored channels, channels are now {watch_channels}")

# Remove channel from message monitoring
@bot.command()
async def _unsub(ctx, *, msg):
    watch_channels.remove(msg)
    await ctx.reply(f"{msg} has been removed from monitored channels, channels are now {watch_channels}")

# Monitor messages sent in channels
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Example: Swear word filter
    # for word in swear_words:
    #     if word in message.content.lower():
    #         await message.delete()
    #         await message.channel.send(f"{message.author.mention} please mind your profanity...")

    # Watch for updates that should be posted to social media
    for channel in watch_channels:
        if message.channel.name == channel:
            print("should send social media message")

    # NOTE: always required, this function is effectively an override allows continued
    # handling of other messages
    await bot.process_commands(message)

# Configure and run the bot
load_config()
bot.run(token=token, log_handler=handler, log_level=logging.DEBUG)