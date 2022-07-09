import datetime
from discord import Colour, Embed
from pycord.wavelink import SearchableTrack


def create_error_embed(title: str, description: str) -> Embed:
    """Creates an error embed

    Parameters:
        title (str): Title of the embed
        description (str): Description of the embed

    Returns:
        Embed: Error embed
    """

    embed = Embed(colour=Colour.red(), title=title, description=description)
    embed.set_thumbnail(url="https://i.imgur.com/T7qpkgH.png")

    return embed


def create_default_embed(
    title: str, description: str = "", thumbnail: str = ""
) -> Embed:
    """Creates a default embed

    Parameters:
        title (str): Title of the embed
        description (str): Description of the embed
        thumbnail (str): Thumbnail of the embed

    Returns:
        Embed: Default embed
    """

    embed = Embed(colour=Colour.blurple(), title=title, description=description)
    embed.set_thumbnail(url=thumbnail) if thumbnail else None

    return embed


def create_music_embed(title: str, song: SearchableTrack) -> Embed:
    """Creates a music embed

    Parameters:
        title (str): Title of the embed
        song (SearchableTrack): Song to be displayed in the embed

    Returns:
        Embed: Music embed
    """

    duration = str(datetime.timedelta(seconds=song.duration)).split(".", maxsplit=1)[0]

    embed = Embed(colour=Colour.blurple(), title=title)
    embed.add_field(name="Title", value=song.title)
    embed.add_field(name="Duration", value=duration)
    embed.add_field(name="Author", value=song.author)

    try:
        embed.set_thumbnail(url=song.thumb) if song.thumb else None
    except AttributeError:
        pass

    return embed
