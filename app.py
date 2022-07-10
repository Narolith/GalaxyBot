import os
from db import DB
from logic.bot import Bot
from pycord.wavelink import Node, Player, Track
from logic.embed import create_music_embed
from timer import Timer

from music_player import MusicPlayer


# Initialize bot
bot = Bot(is_prod=False)
bot.music_player = MusicPlayer(bot)
bot.db = DB(bot)

# Import command cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

# Event Listeners
@bot.event
async def on_wavelink_node_ready(node: Node):
    """Event fired when a node has finished connecting."""

    print(f"Node: <{node.identifier}> is ready!")


@bot.event
async def on_wavelink_track_start(player: Player, track: Track):
    """Event fired when a track starts."""

    print(f"Track: <{track.title}> started playing!")
    embed = create_music_embed("Now Playing", track)
    await bot.music_player.text_channel.send(embed=embed)
    bot.music_player.idle_timer.cancel() if bot.music_player.idle_timer else None
    bot.music_player.idle_timer = None


@bot.event
async def on_wavelink_track_end(player: Player, track: Track, reason: str):
    """Event fired when a track ends."""

    print(f"Track: <{track.title}> has ended!")
    print(reason)
    if reason == "FINISHED":
        await bot.music_player.check_queue()
    bot.music_player.idle_timer = Timer(300, bot.music_player.leave)


# Run bot
bot.run(bot.config.get("DISCORD_TOKEN"))
