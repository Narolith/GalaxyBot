"""
Music player responsible for bot's music functions
"""

from typing import List
from discord import TextChannel
from pycord.wavelink import SearchableTrack
import pycord.wavelink as wavelink

from logic.bot import Bot


class MusicPlayer:
    """Handles bot's music functions"""

    def __init__(self, bot: Bot):
        self.current_song: SearchableTrack = None
        self.voice_client: wavelink.Player = None
        self.text_channel: TextChannel = None
        self.is_playing: bool = False
        self.bot = bot

    async def play(self, song: SearchableTrack) -> None:
        """Plays the provided song"""

        self.current_song = song
        await self.voice_client.play(self.current_song)
        self.is_playing = True

    async def queue_song(self, song: SearchableTrack) -> None:
        """Queues the provided song"""

        self.bot.music_player.voice_client.queue.extend([song])

    async def stop(self) -> None:
        """Stops the music player"""

        self.bot.music_player.voice_client.queue.clear()
        await self.voice_client.stop()
        self.is_playing = False

    async def skip(self) -> None:
        """Skips the current song"""

        await self.bot.music_player.voice_client.stop()
        await self.check_queue()

    async def leave(self) -> None:
        """Leaves the voice channel"""

        self.bot.music_player.voice_client.queue.clear()
        await self.voice_client.stop()
        await self.voice_client.disconnect(force=True)
        self.voice_client = None
        self.is_playing = False

    async def check_queue(self) -> None:
        """Checks the queue for songs to play"""

        if self.bot.music_player.voice_client.queue:
            next_song = self.bot.music_player.voice_client.queue.pop()
            await self.play(next_song)
        else:
            self.is_playing = False

    async def get_queue(self) -> str:
        """Returns the queue as a string"""

        queue = ""
        for idx, song in enumerate(self.bot.music_player.voice_client.queue, 1):
            title: str = song.info.get("title")
            queue += f"{idx} - {title}\n"
        return queue
