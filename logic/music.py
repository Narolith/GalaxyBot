from pycord.wavelink import abc
from logic.bot import Bot
import pycord.wavelink as wavelink
from pycord.wavelink import SearchableTrack
import validators


SUPPORTED_SITES = ["youtube.com", "youtu.be", "soundcloud.com"]

async def get_song(site: str, search: str) -> SearchableTrack:
    """Looks at initial query and searches the right site for song"""

    if site == "soundcloud":
        song = await wavelink.SoundCloudTrack.search(search, return_first=True)
    else:
        song = await wavelink.YouTubeTrack.search(search, return_first=True)

    return song

async def convert_query(bot: Bot, query: str) -> tuple[str, str]:
    """Converts the query to a searchable string"""

    # Check if query is a YouTube or Soundcloud url
    if validators.url(query):
        if any(site in query for site in SUPPORTED_SITES):
            if "&list=" in query:
                query = query.split("&", 1)[0]
            songs = await bot.music_player.voice_client.node.get_tracks(
                abc.Playable, query
            )
            song_title = songs[0].info.get("title") + " - " + songs[0].info.get("author")
            if "soundcloud" in query.lower():
                return ("soundcloud", song_title)
            else:
                return ("youtube", song_title)
        # If url query is not a YouTube or Soundcloud url, return error
        else:
            raise ValueError("Invalid URL")
    else:
        return ("youtube", query)