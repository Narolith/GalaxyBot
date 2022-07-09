from discord import ApplicationContext, Embed, Member, Status, Guild
from logic.embed import create_default_embed


def get_server(ctx: ApplicationContext) -> Guild:
    """Returns the server the command was sent in

    Parameters:
        ctx (ApplicationContext): Context of the command

    Returns:
        Guild: Server the command was sent in
    """

    if ctx.guild is None:
        raise ValueError("Command must be sent in a server")

    return ctx.guild


def get_online_members(server: Guild) -> int:
    """Returns the number of online members in the server

    Parameters:
        server (Guild): Server to get online members from

    Returns:
        int: Number of online members
    """

    return sum(1 for member in server.members if member.status is not Status.offline)


def create_server_embed(server: Guild, members_online: int) -> Embed:
    """Returns an embed with information about the server

    Parameters:
        server (Guild): Server to get information from
        members_online (int): Number of online members

    Returns:
        Embed: Embed with information about the server
    """

    embed = create_default_embed(
        title=server.name,
        thumbnail=server.icon,
    )
    embed.add_field(name="Owner", value=server.owner.name)
    embed.add_field(name="Created", value=server.created_at.date())
    embed.add_field(name="Member Count", value=server.member_count)
    embed.add_field(name="Members Online", value=members_online)

    return embed


def get_member(member: Member | None, ctx: ApplicationContext) -> Member:
    """Returns the member the command was set to target. If none is provided, target the author

    Parameters:
        member (Member | None): Member to target
        ctx (ApplicationContext): Context of the command

    Returns:
        Member: Member the command was set to target
    """

    return ctx.author if member is None else member


def get_member_roles(member: Member) -> str:
    """Returns a string of all roles the member has besides @everyone

    Parameters:
        member (Member): Member to get roles from

    Returns:
        str: String of roles the member has besides @everyone
    """

    roles = [role.name for role in member.roles if role.name != "@everyone"]

    return ", ".join(roles) if roles else "None"


def create_member_embed(member: Member, roles: str) -> Embed:
    """Returns an embed with information about the member

    Parameters:
        member (Member): Member to get information from
        roles (str): String of roles the member has besides @everyone

    Returns:
        Embed: Embed with information about the member
    """

    embed = create_default_embed(
        member.display_name, thumbnail=member.avatar or member.default_avatar
    )
    embed.add_field(name="Joined", value=member.joined_at.date())
    embed.add_field(name="Roles", value=roles)
    embed.add_field(name="Status", value=member.status.value.capitalize())
    embed.add_field(name="Created", value=member.created_at.date())

    return embed
