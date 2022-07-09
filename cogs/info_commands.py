from discord import (
    Cog,
    Member,
    slash_command,
    Bot,
    Option,
    ApplicationContext,
)
from logic import info


class InfoCommands(Cog):
    """Cog that contains commands related to displaying information
    
    Commands:
        - server: Displays information about the server
        - info: Displays information about a user
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command()
    async def server(self, ctx: ApplicationContext) -> None:
        """Displays information about current server
        
        Parameters:
            ctx (ApplicationContext): Context of the command
        """

        try:
            server = info.get_server(ctx)
        except ValueError as err:
            await ctx.respond(err, ephemeral=True)
            return

        members_online = info.get_online_members(server)
        embed = info.create_server_embed(server, members_online)
        await ctx.respond(embed=embed, ephemeral=True)


    @slash_command()
    async def info(
        self,
        ctx: ApplicationContext,
        member: Option(Member, "Member to select", required=False),
    ) -> None:
        """Displays information about a user or yourself if none is provided
        
        Parameters:
            ctx (ApplicationContext): Context of the command
            member (Member): Member to display information about
        """

        member = info.get_member(member, ctx)
        roles = info.get_member_roles(member)
        embed = info.create_member_embed(member, roles)

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: Bot) -> None:
    """Adds cog to bot commands"""

    bot.add_cog(InfoCommands(bot))
