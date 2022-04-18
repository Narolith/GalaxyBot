"""
Cog of birthday related commands
"""

from discord import (
    ApplicationContext,
    Bot,
    Cog,
    Option,
    slash_command,
)

import db
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError
from app import logger


class BirthdayCommands(Cog):
    """Birthday related commands"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command()
    async def add_birthday(
        self,
        ctx: ApplicationContext,
        month: Option(int, "Month", min_value=1, max_value=12),  # noqa: F821
        day: Option(int, "Day", min_value=1, max_value=31),  # noqa: F821
    ):
        """Adds or updates your birthday in the system"""

        # Validate month and day combo
        is_valid = validate_birthday(month, day)
        if not is_valid:
            await ctx.respond(
                "Month and day not valid, please try again", ephemeral=True
            )
            return

        # Checks for birthday and adds or updates in database
        id = ctx.author.id
        username = ctx.author.name
        session: Session = db.Session()
        try:
            birthday: Query = await find_birthday(session, username)
            if birthday.first():
                birthday.update({db.Birthday.month: month, db.Birthday.day: day})
                message = f"Your birthday has been updated to {month}/{day}"
            else:
                birthday = db.Birthday(id=id, username=username, month=month, day=day)
                session.add(birthday)
                message = f"Your birthday has been set to {month}/{day}"
            await ctx.respond(message, ephemeral=True)
            session.commit()
        except SQLAlchemyError as err:
            logger.error(err)
            await ctx.respond(
                "Something went wrong and your birthday was not added/updated"
            )
        finally:
            session.close()

    @slash_command()
    async def check_birthday(self, ctx: ApplicationContext):
        """Looks up birthday and returns it"""

        username = ctx.author.name
        session: Session = db.Session()
        try:
            birthday: db.Birthday = (await find_birthday(session, username)).first()
            if birthday:
                await ctx.respond(
                    f"Your birthday is set to: {birthday.month}/{birthday.day}",
                    ephemeral=True,
                )
            else:
                await ctx.respond(
                    "Your birthday was not found",
                    ephemeral=True,
                )
        except SQLAlchemyError as err:
            logger.error(err)
            await ctx.respond(
                "Something went wrong and your birthday was not retrieved"
            )
        finally:
            session.close()

    @slash_command()
    async def remove_birthday(self, ctx: ApplicationContext):
        """Removes your birthday from the system"""

        # Checks for birthday and removes it from db
        username = ctx.author.name
        session: Session = db.Session()
        try:
            birthday: Query = await find_birthday(session, username)
            if birthday:
                birthday.delete()
                session.commit()
                message = "Your birthday has been deleted"
            else:
                message = "Your birthday was not found"

            await ctx.respond(message, ephemeral=True)
        except SQLAlchemyError as err:
            logger.error(err)
            await ctx.respond(
                "Something went wrong and your birthday was not retrieved"
            )
        finally:
            session.close()


async def find_birthday(session: Session, username: str) -> Query:
    try:
        return session.query(db.Birthday).filter_by(username=username)
    except SQLAlchemyError as err:
        logger.error(err)


def validate_birthday(month: int, day: int):
    """Validates if birthday is a valid date"""

    is_valid = False

    if month in [1, 3, 5, 7, 8, 10, 12]:
        if day in range(1, 31):
            is_valid = True
    elif month in [4, 6, 9, 11]:
        if day in range(1, 30):
            is_valid = True
    elif month == 2:
        if day in range(1, 29):
            is_valid = True

    return is_valid


def setup(bot: Bot):
    """Adds cog to bot commands"""

    bot.add_cog(BirthdayCommands(bot))
