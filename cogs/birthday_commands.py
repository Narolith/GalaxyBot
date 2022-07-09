from discord import (
    ApplicationContext,
    Bot,
    Cog,
    Option,
    slash_command,
)

from sqlalchemy.exc import SQLAlchemyError
import logic.birthday as birthday_logic


class BirthdayCommands(Cog):
    """Birthday related commands

    Commands:
        - add_birthday: Adds a birthday to the database
        - remove_birthday: Removes a birthday from the database
        - check_birthday: Checks if user has a birthday in the database and if so, displays it
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command()
    async def add_birthday(
        self,
        ctx: ApplicationContext,
        month: Option(int, "Month", min_value=1, max_value=12),
        day: Option(int, "Day", min_value=1, max_value=31),
    ) -> None:
        """Adds or updates your birthday in the system

        Parameters:
            ctx (ApplicationContext): Context of the command
            month (int): Month of the birthday
            day (int): Day of the birthday
        """

        try:
            await birthday_logic.add_birthday(self.bot, ctx, month, day)
        except ValueError as err:
            await ctx.respond(err, ephemeral=True)
            return
        except SQLAlchemyError as err:
            await ctx.respond("There was an error adding your birthday", ephemeral=True)
            return
        await ctx.respond("Birthday added successfully", ephemeral=True)

    @slash_command()
    async def check_birthday(self, ctx: ApplicationContext):
        """Looks up birthday and returns it

        Parameters:
            ctx (ApplicationContext): Context of the command
        """

        try:
            birthday = await birthday_logic.get_birthday(self.bot, ctx)
        except ValueError as err:
            await ctx.respond(err, ephemeral=True)
            return
        await ctx.respond(
            f"Your birthday is {birthday.month}/{birthday.day}", ephemeral=True
        )

    @slash_command()
    async def remove_birthday(self, ctx: ApplicationContext):
        """Removes your birthday from the database

        Parameters:
            ctx (ApplicationContext): Context of the command
        """

        try:
            await birthday_logic.remove_birthday(self.bot, ctx)
        except ValueError as err:
            await ctx.respond(err, ephemeral=True)
            return
        except SQLAlchemyError as err:
            await ctx.respond(
                "There was an error removing your birthday", ephemeral=True
            )
            return
        await ctx.respond("Birthday removed", ephemeral=True)


def setup(bot: Bot):
    """Adds cog to bot commands"""

    bot.add_cog(BirthdayCommands(bot))
