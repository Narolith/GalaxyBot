from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import discord
from dotenv import dotenv_values
from pycord import wavelink

from logic.birthday import get_run_time, run_jobs

if TYPE_CHECKING:
    from music_player import MusicPlayer
    from db import DB


class Bot(discord.Bot):
    """Main Bot Class that inherits from discord.Bot

    Attributes:
        config (dict): Bot configuration
        db (DB): Database object
        music_player (MusicPlayer): Music player object
    """

    def __init__(self, is_prod: bool = False):
        super().__init__(
            intents=discord.Intents.all(),
        )
        self.config = get_config(is_prod)

    music_player: MusicPlayer
    db: DB

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")

        await wavelink.NodePool.create_node(
            bot=self,
            host="lavalink.oops.wtf",
            port=2000,
            password="www.freelavalink.ga",
        )

        await run_jobs(self)
        run_time = (datetime.utcnow() + timedelta(seconds=get_run_time()))
        print(f"Jobs scheduled for {run_time} UTC")

def get_config(is_prod: bool) -> dict[str, str]:
    """Returns config env variables. Defaults to dev.

    Parameters:
        is_prod (bool): Whether to return prod or dev config
    """

    return dotenv_values(".prod.env") if is_prod else dotenv_values(".dev.env")
