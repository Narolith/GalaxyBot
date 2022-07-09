from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio
from datetime import datetime, timedelta, tzinfo
from typing import List, Tuple
from db import Birthday as db_Birthday
from discord import ApplicationContext, Guild, Member, Role, TextChannel
import pytz
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from logic.embed import create_default_embed

if TYPE_CHECKING:
    from logic.bot import Bot


###################
# CRUD OPERATIONS #
###################


async def add_birthday(bot: Bot, ctx: ApplicationContext, month: int, day: int) -> None:
    """Adds or updates birthday in database
    Parameters:
        bot: Instance of Bot
        month: Month of birthday
        day: Day of birthday

    Raises:
        SQLAlchemyError if there is an error adding or updating birthday
        ValueError if birthday is invalid
    """

    if validate_birthday(month, day) is False:
        raise ValueError("Invalid birthday")

    session: Session = bot.db.session_maker()
    birthday: db_Birthday = (
        session.query(db_Birthday).filter(db_Birthday.id == ctx.author.id).first()
    )
    if birthday:
        session.delete(birthday)
    birthday = db_Birthday(
        id=ctx.author.id, username=ctx.author.name, month=month, day=day
    )
    session.add(birthday)
    session.commit()
    session.close()


async def remove_birthday(bot: Bot, ctx: ApplicationContext) -> None:
    """Removes birthday from database
    Parameters:
        bot: Instance of Bot
        ctx: Context of message
    Raises:
        SQLAlchemyError if there is an error removing birthday
        ValueError if birthday is not found
    """

    session: Session = bot.db.session_maker()
    birthday: db_Birthday = (
        session.query(db_Birthday).filter(db_Birthday.id == ctx.author.id).first()
    )
    if birthday:
        session.delete(birthday)
        session.commit()
        session.close()
    else:
        session.close()
        raise ValueError("You do not have a birthday set")


async def get_birthday(bot: Bot, ctx: ApplicationContext) -> db_Birthday:
    """Gets birthday from database
    Parameters:
        bot: Instance of Bot
        ctx: Context of message
    Raises:
        ValueError if birthday is not found
    """

    session: Session = bot.db.session_maker()
    birthday: db_Birthday = (
        session.query(db_Birthday).filter(db_Birthday.id == ctx.author.id).first()
    )
    if birthday:
        session.close()
        return birthday
    else:
        session.close()
        raise ValueError("You do not have a birthday set")


async def get_birthdays(bot: Bot, date: Tuple | None = None) -> List[db_Birthday]:
    """Gets all birthdays from database with optional filter
    Parameters:
        bot: Instance of Bot
        date: Optional filter for birthday date

    Raises:
        SQLAlchemyError if there is an error getting birthdays
    """

    session: Session = bot.db.session_maker()
    if date:
        birthdays: List[db_Birthday] = (
            session.query(db_Birthday)
            .filter(db_Birthday.month == date[0], db_Birthday.day == date[1])
            .all()
        )
    else:
        birthdays: List[db_Birthday] = session.query(db_Birthday).all()
    session.close()
    return birthdays


####################
#  BIRTHDAY JOBS   #
####################


async def birthday_message(bot: Bot) -> None:
    """Sends a daily birthday message for all users with a birthday

    Parameters:
        bot: Instance of Bot
    """

    print("running birthday_message")

    month = datetime.utcnow().month
    day = datetime.utcnow().day
    try:
        birthdays: List[db_Birthday] = await get_birthdays(bot, (month, day))
    except SQLAlchemyError as e:
        print(e)
        return

    if birthdays:
        try:
            guild_id: int = int(bot.config.get("GUILD_ID"))
            guild: Guild = bot.get_guild(guild_id)
            channel: TextChannel = guild.system_channel
            role_id: int = int(bot.config.get("GUILD_ANNOUCEMENT_ROLE_ID"))
            announcement_role: Role = guild.get_role(role_id)
        except AttributeError as e:
            print(e)
            return

        try:
            birthday_people: str = get_birthday_people(birthdays, guild)
        except AttributeError as e:
            print(e)
            return

        embed = create_default_embed(
            title="Happy Birthday!",
            description=f"""Please wish a happy birthday
            to the following {announcement_role.mention}!""",
            thumbnail="https://i.imgur.com/2LQPTEO.png",
        )
        embed.add_field(name="Users", value=birthday_people)
        await channel.send(embed=embed)

    print("ran birthday_message")


async def database_cleanup(bot: Bot):
    """Deletes birthdays of users no longer in the server

    Parameters:
        bot: Instance of Bot

    Raises:
        SQLAlchemyError if there is an error deleting birthdays
    """

    print("running database_cleanup")

    try:
        guild_id: int = int(bot.config.get("GUILD_ID"))
        guild: Guild = bot.get_guild(guild_id)
        members: List[Member] = guild.members
    except AttributeError as e:
        print(e)
        return

    session: Session = bot.db.session_maker()
    try:
        birthdays: List[db_Birthday] = await get_birthdays(bot)
    except SQLAlchemyError as e:
        print(e)
        return

    for birthday in birthdays:
        if birthday.id not in [member.id for member in members]:
            session.delete(birthday)
    session.commit()
    session.close()

    print("ran database_cleanup")


####################
#  HELPER METHODS  #
####################

# Get list of users with birthday
def get_birthday_people(birthdays: List[db_Birthday], guild: Guild) -> str:
    """Returns a string of all the birthday people

    Parameters:
        birthdays: List of birthdays
        guild: Guild of the server

    Returns:
        String of all the birthday people

    Raises:
        AttributeError if there is an error getting members
    """

    birthday_people: str = ""
    for birthday in birthdays:
        member: Member = guild.get_member(int(birthday.id))
        birthday_people += f"{member.mention}\n"
    return birthday_people


# Run database cleanup and birthday message jobs every day
async def run_jobs(bot: Bot) -> None:
    """Runs database cleanup and birthday message jobs every day

    Parameters:
        bot: Instance of Bot
    """

    # Run every day at 10am eastern time on separate thread
    while bot.is_ready():
        await asyncio.sleep(delay=get_run_time())
        await database_cleanup(bot)
        await birthday_message(bot)
        await run_jobs(bot)


def get_run_time() -> float:
    """Sets run time for daily birthday jobs

    Returns:
        float of seconds to wait before running jobs
    """

    date = datetime(
        datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day, 14, 0
    )
    if datetime.utcnow().hour >= 14:
        date += timedelta(days=1)
    return (date - datetime.utcnow()).total_seconds()


def validate_birthday(month: int, day: int) -> bool:
    """Validates if birthday is a valid date

    Parameters:
        month: Month of birthday
        day: Day of birthday

    Returns:
        True if birthday is valid, False if not
    """

    return (
        True
        if (
            month == 2
            and day <= 29
            or month in (1, 3, 5, 7, 8, 10, 12)
            and day <= 31
            or month in (4, 6, 9, 11)
            and day <= 30
        )
        else False
    )
