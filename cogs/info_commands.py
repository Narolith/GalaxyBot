"""
Cog containing information related commands
"""


from discord import (
    Cog,
    Colour,
    Embed,
    Member,
    Status,
    slash_command,
    Bot,
    Option,
    ApplicationContext,
)

from utils.embed import EmbedCreator


class InfoCommands(Cog):
    """Cog that contains commands related to displaying information"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command()
    async def server(self, ctx: ApplicationContext):
        """Displays information about current server"""
        server = ctx.guild

        if server is None:
            return ctx.respond("Could not find information on the current server")

        members_online = 0

        for member in server.members:
            if member.status != Status.offline:
                members_online += 1

        embed = Embed(
            title=server.name,
            colour=Colour.blue(),
        )
        embed.set_thumbnail(url=server.icon)
        embed.add_field(name="Owner", value=server.owner.name).add_field(
            name="Created", value=server.created_at.date()
        ).add_field(name="Member Count", value=server.member_count).add_field(
            name="Members Online", value=members_online
        )

        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command()
    async def info(
        self,
        ctx: ApplicationContext,
        member: Option(Member, "Member to select", required=False),  # noqa: F722
    ):
        """Displays information about a user or yourself if none is provided"""

        # If member is not provided, target the author
        if member is None:
            member: Member = ctx.author

        # Builds list of member roles besides @everyone
        roles = ""
        for role in member.roles:
            if role.name == "@everyone":
                continue
            roles += f"{role.name}\n"

        # Build embed message with information
        embed = EmbedCreator.embed(
            member.display_name, thumbnail=member.avatar or member.default_avatar
        )

        embed.add_field(name="Joined", value=member.joined_at.date()).add_field(
            name="Roles", value=roles
        ).add_field(name="Status", value=member.status.value.capitalize()).add_field(
            name="Created", value=member.created_at.date()
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: Bot):
    """Adds cog to bot commands"""

    bot.add_cog(InfoCommands(bot))
