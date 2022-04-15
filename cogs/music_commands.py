from discord import ApplicationContext, Bot, Cog, Option, slash_command
import pycord.wavelink as wavelink
from wavelink import SearchableTrack, abc
from app import music_player
from utils.embed import EmbedCreator


class Music(Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: Bot):
        self.bot = bot
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""

        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(
            bot=self.bot,
            host="lavalink.islantay.tk",
            port=8880,
            password="waifufufufu",
        )

    @Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""

        print(f"Node: <{node.identifier}> is ready!")

    @slash_command()
    async def play(
        self,
        ctx: ApplicationContext,
        query: Option(
            str, "Name of song, YouTube, or Soundcloud link", required=True  # noqa F722
        ),
    ):
        """Searches for a song and then plays or queues it.
        Will join voice channel if not already in it"""

        if not ctx.author.voice:
            embed = EmbedCreator.error_embed(
                "Not in voice channel", "You are not in a voice channel!"
            )
            return await ctx.respond(embed=embed)
        music_player.text_channel = ctx.channel

        embed = EmbedCreator.embed("Looking up song", f"Looking for:\n{query}")
        await ctx.respond(embed=embed)

        # Checks if connected to a voice client and connects if not
        if not ctx.voice_client:
            music_player.voice_client = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            music_player.voice_client = ctx.voice_client

        # Reads query string to identify urls to look up song information
        # Currently only YouTube and Soundcloud urls are supported
        song: SearchableTrack
        song_title = ""
        if any(sub_string in query for sub_string in ["http://", "https://"]):
            if any(
                site in query
                for site in ["youtu.be", "www.youtube.com", "soundcloud.com"]
            ):
                songs = await music_player.voice_client.node.get_tracks(
                    abc.Playable, query
                )
                song_title = songs[0].info.get("title")
            else:
                embed = EmbedCreator.error_embed(
                    "Unsupported Site", "Links to this site aren't supported"
                )
                return await ctx.respond(embed=embed)

        # Looks up song based on type and defaults to YouTube if none found
        song = await get_song(query, song_title or query)

        # Adds to queue and if already playing, send message to notify
        # user that the song has been added to a queue.  This is not
        # done for the song if music is not playing even though it
        # is added to queue as it will being to play immediately
        if music_player.voice_client.is_playing():
            embed = EmbedCreator.music_embed("Added to queue", song)
            await ctx.respond(embed=embed)

        music_player.queue.append(song)
        music_player.is_stopped = False

    @slash_command()
    async def stop(self, ctx: ApplicationContext):
        """Stops the music player"""

        # Checks if music is playing and stops if so.  AttributeError catch
        # in case this is called prior to a voice_client existing
        try:
            if music_player.voice_client.is_playing():
                await music_player.voice_client.stop()
                music_player.is_stopped = True
                music_player.queue.clear()
                embed = EmbedCreator.embed("Player stopped", "Player has been stopped")
                await ctx.respond(embed=embed)
            else:
                embed = EmbedCreator.error_embed(
                    "Not Playing", "I am not playing music!"
                )
                await ctx.respond(embed=embed)
        except AttributeError:
            pass

    @slash_command()
    async def leave(self, ctx: ApplicationContext):
        """Leaves the voice channel if in one"""

        if music_player.voice_client:
            await music_player.voice_client.disconnect(force=True)
            embed = EmbedCreator.embed(
                "Leaving Room", "Hope you had a great time! I'll head out."
            )
            await ctx.respond(embed=embed)
        else:
            embed = EmbedCreator.error_embed(
                "Not in channel", "I am currently not in a channel!"
            )
            await ctx.respond(embed=embed)

    @slash_command()
    async def list(self, ctx: ApplicationContext):
        """Displays the songs in queue"""

        song_list: str = ""
        for idx, song in enumerate(music_player.queue):
            title: str = song.info.get("title")
            song_list += f"{idx + 1} - {title}\n"
        embed = EmbedCreator.embed("Songs in Queue", song_list)

        await ctx.respond(embed=embed)

    @slash_command()
    async def skip(self, ctx: ApplicationContext):
        """Skips the current song and stops player if queue is empty"""

        try:
            if music_player.voice_client.is_playing():
                if not music_player.queue:
                    embed = EmbedCreator.embed(
                        "Player stopped", "No songs in queue, stopping player."
                    )
                    await ctx.respond(embed=embed)
                    await self.stop(ctx)
                else:
                    song = music_player.current_song
                    embed = EmbedCreator.music_embed("Skipped", song)
                    await ctx.respond(embed=embed)
                    await music_player.voice_client.stop()
            else:
                embed = EmbedCreator.error_embed(
                    "Not playing", "I am not playing music!"
                )
                await ctx.respond(embed=embed)
        except AttributeError:
            pass


def setup(bot: Bot):
    bot.add_cog(Music(bot))


async def get_song(query: str, search: str) -> SearchableTrack:
    """Looks at initial query and searches the right site for song"""

    if "soundcloud" in query:
        song = await wavelink.SoundCloudTrack.search(search, return_first=True)
    else:
        song = await wavelink.YouTubeTrack.search(search, return_first=True)

    return song
