import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

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

twitter = {}

# Set up bot to listen for prefix commands
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name}, reporting for duty!")

secret_role = "cool kid"

@bot.event
async def on_member_join(member):
    # Will send as a DM; how to send as a reply??
    await member.send(f"Welcome to the server {member.name}")

# DM user who uses the !hello command
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}!")

# Assign the "cool kid" role to anyone who uses the !hello command
# NOTE: A bot cannot assign a role that is higher in the roles heirarchy in Discord settings
@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
    else:
        await ctx.send(f"{secret_role} doesn't exist!f")

# Assign the "cool kid" role to anyone who uses the !remove command
@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)

    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} is now removed from {secret_role}")
    else:
        await ctx.send(f"{secret_role} doesn't exist!f")

# Send a message to any user who has the "cool kid" role and uses the !secret command  a message
@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")

# Handle any errors thrown from the secret function
# NOTE: Errors have to be handled this way for commands that use the has_role limiter
@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")

# DM a user whatever the sent using the !dm {msg} command
@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

# Reply to a user using the !reply command
@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

# Create a fake poll using a thumbs up and thumbs down emojis
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")