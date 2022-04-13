"""
Music player responsible for bot's music functions
"""

from discord import Bot, TextChannel
from discord.ext import tasks
from typing import List
from wavelink import SearchableTrack
import pycord.wavelink as wavelink

from utils.embed import EmbedCreator


class MusicPlayer:
    """Handles bot's music functions"""

    def __init__(self, bot: Bot):
        self.current_song: SearchableTrack = None
        self.queue: List[SearchableTrack] = []
        self.check_player.start()
        self.voice_client: wavelink.Player = None
        self.text_channel: TextChannel = None
        self.bot: Bot = bot
        self.is_stopped = True

    @tasks.loop(seconds=1)
    async def check_player(self):
        try:
            if not self.voice_client.is_playing():
                if self.is_stopped:
                    self.current_song = None
                else:
                    await self.play_song()
        except AttributeError:
            pass

    @check_player.before_loop
    async def before_check_player(self):
        await self.bot.wait_until_ready()

    async def play_song(self):
        if self.queue:
            self.current_song = self.queue.pop(0)
            await self.voice_client.play(self.current_song)
            embed = EmbedCreator.music_embed("Now Playing", self.current_song)
            await self.text_channel.send(embed=embed)
