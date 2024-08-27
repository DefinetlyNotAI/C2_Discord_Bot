import json
import os
import discord
from discord.ext import commands
from Logicytics import log, Logicytics


# Function to read secret keys and information from JSON file
def read_key():
    """
    Attempts to read and parse the 'api.json' file to extract configuration settings.

    The function checks if the file exists, is in the correct format, and contains the required keys. It then returns
    a tuple containing the extracted configuration values.

    Returns:
        tuple: A tuple containing the extracted configuration values:
            - token (str): The token value from the 'api.json' file.
            - channel_id (int): The channel ID value from the 'api.json' file.
            - webhooks_username (str): The webhooks username value from the 'api.json' file.
            - limit_of_messages_to_check (int): The limit of messages to check value from the 'api.json' file.
            - log_using_debug? (bool): The log using debug value from the 'api.json' file.
    """
    try:
        with open("api.json", "r") as f:
            config = json.load(f)
        if (
                config is not None
                and isinstance(config["token"], str)
                and isinstance(config["channel_id_(for_c2_commands)"], int)
                and isinstance(config["channel_id_(for_c2_actions)"], int)
                and isinstance(config["channel_id_(for_logs)"], int)
                and isinstance(config["webhooks_username"], list)
                and isinstance(config["log_using_debug?"], bool)
        ):
            return (
                config["token"],
                config["channel_id_(for_c2_commands)"],
                config["channel_id_(for_c2_actions)"],
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
TOKEN, CHANNEL_ID_COMMANDS, CHANNEL_ID_LOGS, CHANNEL_ID_ACTIONS, WEBHOOK_USERNAME, DEBUG = read_key()

MENU = """
Reactions Menu:

⚙️ -> Restart
🛜 -> Change DNS to 127.0.0.1 (WARNING: This will disconnect the connection forever!)
🪝 -> Download Logicytics and run
📃 -> Send Logicytics Logs
💣 -> Destroy device
📤 -> Upload a file of your choice (WIP)
📥 -> Download a file of your choice (WIP)
"""


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    """
    Event handler triggered when the bot is fully connected and ready.

    This function is called when the bot has finished connecting to Discord and
    is ready to start accepting commands and events.

    Parameters:
    None

    Returns:
    None
    """
    log.info(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    """
    Event handler triggered when a message is received, with checks of the author.

    Parameters:
        message (discord.Message): The message object containing information about the message.

    Returns:
        None
    """
    channel_c2 = await message.guild.fetch_channel(CHANNEL_ID_COMMANDS)
    channel_actions = await message.guild.fetch_channel(CHANNEL_ID_ACTIONS)
    channel_log = await message.guild.fetch_channel(CHANNEL_ID_LOGS)
    log.info(channel_actions.history(limit=1))
    if not channel_actions.history(limit=1):
        log.info(f"Starting C2")
        await message.channel.send("React to this message to start the C2. More info should be sent to the other C2 channel, refrain from sending messages here.")

    if isinstance(channel_c2, discord.TextChannel) and isinstance(channel_log, discord.TextChannel):
        if message.author != bot.user:
            # Check if the message author is not the bot
            log.info(f"Message from {message.author}: {message.content}")
        if message.content == "/c2" and message.author != bot.user:
            if message.author == message.guild.owner or message.author.guild_permissions.administrator:
                await message.channel.send("/c2 logs -> Retrieves and sends the bots logs to a specified channel. \n/c2 menu -> Sends possible reaction menu")
            else:
                await message.channel.send("You do not have permission to use this command?")
                log.error(f"User {message.author} attempted to use the /c2 command. Invalid permission's.")
        if message.content == "/c2 logs" and message.author != bot.user:
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
            if message.author == message.guild.owner or message.author.guild_permissions.administrator:
                await message.channel.send(MENU)
            else:
                await message.channel.send("You do not have permission to use this command?")
                log.error(f"User {message.author} attempted to use the menu command. Invalid permission's.")
        if str(message.author) not in WEBHOOK_USERNAME:
            # Check if the message author is not the bot
            log.info(f"Message Ignored due to {message.author} not being in the allowed list of users: {WEBHOOK_USERNAME}")
    else:
        log.critical(
            f"Channel {CHANNEL_ID_COMMANDS} or {CHANNEL_ID_LOGS} not found as text channels. Bot Crashed."
        )
        exit(1)


async def logs(ctx):
    """
    Retrieves and sends the Discord logs to a specified channel.

    Parameters:
    ctx (discord.ext.commands.Context): The context of the command invocation.

    Returns:
    None
    """
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


bot.run(TOKEN, log_handler=None)
