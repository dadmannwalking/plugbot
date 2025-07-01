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
        # TODO: Handle listing both channel IDs and channel names
        if config.watched_channels:
            channels_list = "\n".join(f"`{cid}`" for cid in config.watched_channels)
            await ctx.reply(f"Currently monitored channels:\n{channels_list}")
        else:
            await ctx.reply("No channels are currently being monitored.")
        return

    if len(components) == 2 and components[0] in ["add", "remove"]:
        # TODO: Handle accepting both channel IDs and channel names; should print out both channel name and ID, but only add channel ID to config
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
async def filters(ctx, *, msg):
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

# List, add, or remove users from the list of monitored users
@bot.command()
async def users(ctx, *, msg):
    config = get_config(ctx.guild.id)
    if config.authorized(ctx.author, ctx.guild) == False:
        return

    components = msg.strip().split()
    action = components[0]

    if action == "list":
        if config.permitted_users:
            users_list = "\n".join(
                f"{member.display_name} ({member.id})" if (member := ctx.guild.get_member(user_id)) 
                else f"Unknown User ({user_id})"
                for user_id in config.permitted_users
            )
            await ctx.reply(f"Currently reposting messages from these users:\n{users_list}")
        else:
            await ctx.reply("Messages from all users in monitored channels are currently being reposted.")
        return
    
    if len(components) == 2 and action in ["add", "remove"]:
        identifier = components[1].strip().lower()
        found_user = None

        try: 
            user_id = int(identifier)
            found_user = next((user for user in ctx.guild.members if user.id == user_id), None)
        except Exception as e:
            found_user = next(
                (user for user in ctx.guild.members 
                 if (user.name.lower() == identifier or user.display_name.lower() == identifier)), 
                 None
            )

        if found_user is None:
            return await ctx.reply(f"User {components[1]} not found in guild.")

        user_string = f"{found_user.display_name} ({found_user.id})"

        if action == "add":
            if found_user.id in config.permitted_users:
                return await ctx.reply(f"`{user_string}` already monitored.")
            
            config.permitted_users.append(found_user.id)
            set_config(config, ctx.guild.id)
            return await ctx.reply(f"Added `{user_string}` to monitored users.")

        if action == "remove":
            if found_user.id not in config.permitted_users:
                return await ctx.reply(f"`{user_string}` not monitored.")

            config.permitted_users.remove(found_user.id)
            set_config(config, ctx.guild.id)
            return await ctx.reply(f"Removed `{user_string}` from monitored users.")

    await ctx.reply(f"unable to parse command parameters: `{msg}`")

# Get and print message history
@bot.command()
async def gethistory(ctx, *, msg):
    def escape_md(text):
        if not text:
            return ""
        return text.replace('`', '\\`')

    config = get_config(ctx.guild.id)

    if config.authorized(ctx.author, ctx.guild) == False:
        return

    try:
        limit = int(msg.strip())
        valid_messages_found = False
        async for message in ctx.channel.history(limit=limit):
            title, desc, url, thumb = msghelper.handle(message)
            message_json = msghelper.json_from(message)
            
            if config.confirm(message, message_json, True) == False:
                taglog(f"skipping message with json: {message_json}")
                continue

            valid_messages_found = True
            await ctx.reply(
                f"```"
                f"Valid message found with JSON:\n{escape_md(message_json)}\n\n"
                f"Would send message to socials with the following data:\n"
                f"title: {escape_md(title)}\n"
                f"description: {escape_md(desc)}\n"
                f"url: {escape_md(url)}\n"
                f"thumbnail: {escape_md(thumb)}"
                f"```"
            )
        
        if not valid_messages_found:
            await ctx.reply("No valid messages were found in this channel.")
        else:
            await ctx.reply("And that's all I found.")
    except ValueError as e:
        return await ctx.reply(f"{msg} is not a valid number!")

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

@bot.event
async def on_guild_remove(guild):
    print(f"{guild.name} has removed plugbot [{guild.id}]")

@bot.event
async def on_guild_remove(member):
    print(f"{member.name} has joined {member.guild.id}]")

@bot.event
async def on_member_remove(member):
    print(f"{member.name} has left/been removed from {member.guild.id}]")

# Monitor messages sent in channels
@bot.event
async def on_message(message):
    config = get_config(message.guild.id)

    if config.confirm(message, msghelper.json_from(message)) == False:
        taglog(f'user not authorized, process {message.content}')
        await bot.process_commands(message)
        return
    
    if config.bluesky.enabled:
        print("posting to Bluesky...")
        title, description, url, thumbnail = msghelper.handle(message)
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