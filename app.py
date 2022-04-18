"""
Main App File
"""

from datetime import datetime
import logging
import os
from dotenv import dotenv_values
import discord
from music_player import MusicPlayer

from utils.birthday import daily_birthday_jobs, set_run_time

# Load configuration from .env
config = dotenv_values(".env")

# Configure Logging
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename=f"logs/discord-{datetime.now()}.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

bot = discord.Bot(debug_guilds=[785658574474969088], intents=discord.Intents.all())
music_player = MusicPlayer(bot)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    """Event fires once once bot is logged in"""

    print(f"Logged in as {bot.user}")

    # Sets initial runtime for birthday jobs
    # Birthday jobs run at 10am
    # Runs same day if before 10am
    if datetime.now().hour > 9:
        bot.birthday_job_runtime = set_run_time(1)
    else:
        bot.birthday_job_runtime = set_run_time()
    await daily_birthday_jobs.start(bot)


bot.run(config.get("DISCORD_TOKEN"))
