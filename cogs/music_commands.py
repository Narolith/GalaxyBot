from discord import ApplicationContext, Cog, Option, slash_command
from logic.embed import create_music_embed, create_error_embed, create_default_embed
from pycord import wavelink
from pycord.wavelink import SearchableTrack
from logic.music import convert_query, get_song
from logic.bot import Bot
from timer import Timer


class Music(Cog):
    """Music cog to hold Wavelink related commands and listeners.

    Commands:
        - play: Play a song
        - stop: Stop the music player
        - leave: Leave the voice channel
        - list: List all songs in the queue
        - skip: Skip the current song
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command()
    async def play(
        self,
        ctx: ApplicationContext,
        query: Option(str, "Name of song, YouTube, or Soundcloud link", required=True),
    ) -> None:
        """Searches for a song and then plays or queues it.
        Will join voice channel if not already in it

        Parameters:
            ctx (ApplicationContext): Context of the command
            query (str): Name of song, YouTube, or Soundcloud link
        """

        # Check if music player is ready
        if self.bot.music_player is None:
            await ctx.respond(
                embed=create_error_embed(
                    "Music Player Not Ready",
                    "Music player is not ready. Please try again later",
                ),
                ephemeral=True,
            )
            return

        # Get the voice channel
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None

        # Check if the user is in a voice channel
        if voice_channel is None:
            await ctx.respond(
                embed=create_error_embed(
                    "Bot Not In Voice Channel",
                    "You must be in a voice channel to use this command.",
                ),
                ephemeral=True,
            )
            return

        # Check if bot is already in user's voice channel and join if not
        if self.bot.music_player.voice_client is None:
            self.bot.music_player.voice_client = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        elif self.bot.music_player.voice_client.channel != voice_channel:
            await self.bot.music_player.voice_client.move_to(voice_channel)

        # Set music player text channel to the channel the command was sent in
        self.bot.music_player.text_channel = ctx.channel

        # Initial response to user
        await ctx.respond(
            embed=create_default_embed("Looking up song", f"Looking for:\n{query}")
        )

        # Reads query string to identify urls to look up song information
        # Currently only YouTube and Soundcloud urls are supported
        song: SearchableTrack
        try:
            song_info = await convert_query(self.bot, query)
        except ValueError:
            await ctx.respond(
                embed=create_error_embed(
                    "Invalid URL", "Only YouTube and Soundcloud URLs are supported."
                ),
                ephemeral=True,
            )
            return
        # Looks up song based on type and defaults to YouTube if none found
        song = await get_song(*song_info)

        # If song is not found, return error
        if song is None:
            await ctx.respond(
                embed=create_error_embed(
                    "Song not found", "The song you requested was not found."
                ),
                ephemeral=True,
            )
            return

        # If music player is not playing, play song
        if self.bot.music_player.is_playing is False:
            await self.bot.music_player.play(song)

        # If music player is playing, queue song
        else:
            self.bot.music_player.voice_client.queue.extend([song])
            await ctx.respond(embed=create_music_embed("Song Queued", song))

    @slash_command()
    async def stop(self, ctx: ApplicationContext):
        """Stops the music player"""

        await self.bot.music_player.stop()
        await ctx.respond(
            embed=create_default_embed("Stopped", "Stopped the music player")
        )

    @slash_command()
    async def leave(self, ctx: ApplicationContext):
        """Leaves the voice channel if in one"""

        if self.bot.music_player.voice_client is not None:
            await self.bot.music_player.leave()
            await ctx.respond(
                embed=create_default_embed("Left Channel", "Left the voice channel")
            )
        else:
            await ctx.respond(
                embed=create_error_embed(
                    "Not in a voice channel",
                    "I am not in a voice channel!.",
                ),
                ephemeral=True,
            )

    @slash_command()
    async def join(self, ctx: ApplicationContext):
        """Joins the music player to the voice channel the user is in"""

        # Get the voice channel
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None

        # Check if the user is in a voice channel
        if voice_channel is None:
            await ctx.respond(
                embed=create_error_embed(
                    "Not in a voice channel",
                    "You must be in a voice channel to use this command.",
                ),
                ephemeral=True,
            )
            return

        if self.bot.music_player.voice_client is None:
            self.bot.music_player.voice_client = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            await self.bot.music_player.voice_client.move_to(voice_channel)

        await ctx.respond(
            embed=create_default_embed("Joined", "Joined the voice channel")
        )
        self.bot.music_player.text_channel = ctx.channel
        if self.bot.music_player.is_playing is False:
            self.bot.music_player.idle_timer = Timer(300, self.bot.music_player.leave)

    @slash_command()
    async def list(self, ctx: ApplicationContext):
        """Displays the songs in queue"""

        song_list = self.bot.music_player.get_queue()
        embed = create_default_embed("Songs in Queue", song_list)

        await ctx.respond(embed=embed)

    @slash_command()
    async def skip(self, ctx: ApplicationContext):
        """Skips the current song and stops player if queue is empty"""

        await ctx.respond(
            embed=create_music_embed("Skipping", self.bot.music_player.current_song)
        )
        await self.bot.music_player.skip()


def setup(bot: Bot):
    bot.add_cog(Music(bot))
