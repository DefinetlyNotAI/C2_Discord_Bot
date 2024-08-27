import json
import os
import colorlog
import discord
from discord.ext import commands
from datetime import datetime


# Log class

class Log:
    def __init__(
            self,
            filename="C2.log",
            err_filename=None,
            use_colorlog=True,
            debug=False,
            debug_color="cyan",
            info_color="green",
            warning_color="yellow",
            error_color="red",
            critical_color="red",
            colorlog_fmt_parameters="%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    ):
        """
        Initializes a new instance of the LOG class.

        The log class logs every interaction when called in both colorlog and in the log File

        Best to only modify filename, and DEBUG.

        Only if you are planning to use the dual-log parameter that allows you to both log unto the shell and the log
        File: IMPORTANT: This class requires colorlog to be installed and also uses it in the INFO level, To use the
        DEBUG level, set DEBUG to True.

            If you are using colorlog, DO NOT INITIALIZE IT MANUALLY, USE THE LOG CLASS PARAMETER'S INSTEAD.
            Sorry for any inconvenience that may arise.

        Args: filename (str, optional): The name of the log File. Defaults to "Server.log". use_colorlog (bool,
        optional): Whether to use colorlog. Defaults to True. debug (bool, optional): Whether to use the DEBUG level.
        Defaults to False (which uses the INFO level). debug_color (str, optional): The color of the DEBUG level.
        Defaults to "cyan". info_color (str, optional): The color of the info level. Defaults to "green".
        warning_color (str, optional): The color of the warning level. Defaults to "yellow". error_color (str,
        optional): The color of the error level. Defaults to "red". critical_color (str, optional): The color of the
        critical level. Defaults to "red". colorlog_fmt_parameters (str, optional): The format of the log message.
        Defaults to "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s".

        Returns:
            None
        """
        self.level = debug
        self.color = use_colorlog
        if self.color:
            # Configure colorlog for logging messages with colors
            logger = colorlog.getLogger()
            if debug:
                logger.setLevel(
                    colorlog.DEBUG
                )  # Set the log level to DEBUG to capture all relevant logs
            else:
                logger.setLevel(
                    colorlog.INFO
                )  # Set the log level to INFO to capture all relevant logs
            handler = colorlog.StreamHandler()
            formatter = colorlog.ColoredFormatter(
                colorlog_fmt_parameters,
                datefmt=None,
                reset=True,
                log_colors={
                    "DEBUG": debug_color,
                    "INFO": info_color,
                    "WARNING": warning_color,
                    "ERROR": error_color,
                    "CRITICAL": critical_color,
                },
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        self.filename = str(filename)
        if err_filename is None:
            self.err_filename = self.filename
        else:
            self.err_filename = str(err_filename)
        if not os.path.exists(self.filename):
            self.__only("|" + "-" * 19 + "|" + "-" * 13 + "|" + "-" * 152 + "|")
            self.__only(
                "|     Timestamp     |  LOG Level  |"
                + " " * 70
                + "LOG Messages"
                + " " * 70
                + "|"
            )
            self.__only("|" + "-" * 19 + "|" + "-" * 13 + "|" + "-" * 152 + "|")

    @staticmethod
    def __timestamp() -> str:
        """
        Returns the current timestamp as a string in the format 'YYYY-MM-DD HH:MM:SS'.

        Returns:
            str: The current timestamp.
        """
        now = datetime.now()
        time = f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
        return time

    def __only(self, message):
        """
        Logs a quick message to the log File.

        Args:
            message: The message to be logged.

        Returns:
            None
        """
        with open(self.filename, "a") as f:
            f.write(f"{str(message)}\n")

    @staticmethod
    def __pad_message(message):
        """
        Adds spaces to the end of a message until its length is exactly 153 characters.

        Parameters:
        - message (str): The input message string.

        Returns:
        - str: The padded message with a length of exactly 153 characters.
        """
        # Calculate the number of spaces needed
        num_spaces = 151 - len(message)

        if num_spaces > 0:
            # If the message is shorter than 153 characters, add spaces to the end
            padded_message = message + " " * num_spaces
        else:
            # If the message is already longer than 153 characters, truncate it to the first 148 characters
            padded_message = message[:148]
            padded_message += "..."

        padded_message += "|"
        return padded_message

    def debug(self, message):
        """
        Logs an debug message via colorlog

        Args:
            message: The message to be logged.

        Returns:
            None
        """
        if self.level:
            colorlog.debug(message)

    def info(self, message):
        """
        Logs an informational message to the log File.

        Args:
            message: The message to be logged.

        Returns:
            None
        """
        if self.color:
            colorlog.info(message)
        with open(self.filename, "a") as f:
            f.write(
                f"[{self.__timestamp()}] > INFO:     | {self.__pad_message(str(message))}\n"
            )

    def warning(self, message):
        """
        Logs a warning message to the log File.

        Args:
            message: The warning message to be logged.

        Returns:
            None
        """
        if self.color:
            colorlog.warning(message)
        with open(self.filename, "a") as f:
            f.write(
                f"[{self.__timestamp()}] > WARNING:  | {self.__pad_message(str(message))}\n"
            )

    def error(self, message):
        """
        Logs an error message to the log File.

        Args:
            message: The error message to be logged.

        Returns:
            None
        """
        if self.color:
            colorlog.error(message)
        with open(self.err_filename, "a") as f:
            f.write(
                f"[{self.__timestamp()}] > ERROR:    | {self.__pad_message(str(message))}\n"
            )

    def critical(self, message):
        """
        Logs a critical message to the error log File.

        Args:
            message: The critical message to be logged.

        Returns:
            None
        """
        if self.color:
            colorlog.critical(message)
        with open(self.err_filename, "a") as f:
            f.write(
                f"[{self.__timestamp()}] > CRITICAL: | {self.__pad_message(str(message))}\n"
            )


# Configure colorlog for logging messages with colors
log = Log()


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
                and isinstance(config["channel_id_(for_c2)"], int)
                and isinstance(config["channel_id_(for_logs)"], int)
                and isinstance(config["webhooks_username"], list)
                and isinstance(config["log_using_debug?"], bool)
        ):
            return (
                config["token"],
                config["channel_id_(for_c2)"],
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
TOKEN, CHANNEL_ID_PCAPS, CHANNEL_ID_LOGS, WEBHOOK_USERNAME, DEBUG = read_key()

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
    channel_pcaps = await message.guild.fetch_channel(CHANNEL_ID_PCAPS)
    channel_log = await message.guild.fetch_channel(CHANNEL_ID_LOGS)
    if isinstance(channel_pcaps, discord.TextChannel) and isinstance(
            channel_log, discord.TextChannel
    ):
        log.info(f"Message from {message.author}: {message.content}")
        if message.content == "/logs c2":
            if (
                    message.author == message.guild.owner
                    or message.author.guild_permissions.administrator
            ):
                if message.channel.id == CHANNEL_ID_LOGS:
                    await logs(message.channel)
                else:
                    await message.channel.send(
                        "This is not the logs preconfigured channel. Please use the /logs command in the logs channel."
                    )
                    log.warning(
                        f"Channel {message.channel} is not the one preconfigured."
                    )
            else:
                await message.channel.send(
                    "You do not have permission to use this command?"
                )
                log.error(
                    f"User {message.author} attempted to use the /logs command. Invalid permission's."
                )
        elif str(message.author) in WEBHOOK_USERNAME:
            pass
            # await extract_and_decrypt(CHANNEL_ID_PCAPS)
        elif str(message.author) not in WEBHOOK_USERNAME and message.author != bot.user:
            log.info(
                f"Message Ignored due to {message.author} not being in the allowed list of users: {WEBHOOK_USERNAME}"
            )
    else:
        log.critical(
            f"Channel {CHANNEL_ID_PCAPS} or {CHANNEL_ID_LOGS} not found as text channels. Bot Crashed."
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
