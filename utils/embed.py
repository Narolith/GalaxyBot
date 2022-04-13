"""
For Embed related utilities
"""

import datetime
from discord import Colour, Embed
from wavelink import SearchableTrack


class EmbedCreator:
    """Responsible for creating different embeds"""

    @staticmethod
    def error_embed(title: str, description: str):
        """Creates an error embed"""

        embed = Embed(
            colour=Colour.red, title=title, description=description
        ).set_thumbnail(url="https://i.imgur.com/T7qpkgH.png")

        return embed

    @staticmethod
    def embed(title: str, description: str, thumbnail: str = ""):
        """Creates a default embed"""

        embed = Embed(colour=Colour.blurple(), title=title, description=description)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        return embed

    @staticmethod
    def music_embed(title: str, song: SearchableTrack):
        """Creates a music embed"""

        duration = datetime.timedelta(seconds=song.duration)

        embed = Embed(colour=Colour.blurple(), title=title)
        embed.add_field(name="Title", value=song.title)
        embed.add_field(name="Duration", value=duration)
        embed.add_field(name="Author", value=song.author)

        try:
            if song.thumb:
                embed.set_thumbnail(url=song.thumb)
        except AttributeError:
            pass

        return embed
