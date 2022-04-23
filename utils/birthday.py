from asyncio.log import logger
from datetime import datetime, timedelta
from typing import List

from discord import Bot, Embed, Guild, Member, Role, TextChannel
from discord.ext import tasks

import db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from mysql.connector.errors import OperationalError


# Prod Ids
# GUILD_ID = 398266931678806017
# GUILD_ANNOUCEMENT_ROLE_ID = 751548638387372083

# Dev Ids
GUILD_ID = 785658574474969088
GUILD_ANNOUCEMENT_ROLE_ID = 808486552443289630


@tasks.loop(seconds=1.0)
async def daily_birthday_jobs(bot: Bot):
    """Schedules daily birthday message and cleanup"""

    date = datetime.now()
    if date > bot.birthday_job_runtime:
        await database_cleanup(bot)
        await birthday_message(bot)
        bot.birthday_job_runtime = set_run_time(1)


def set_run_time(days_to_add: int = 0):
    """Sets run time for daily birthday jobs"""

    current_date = datetime.now()
    return current_date.replace(
        day=current_date.day, hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=days_to_add)


async def database_cleanup(bot: Bot):
    """Deletes stale birthdays in database"""

    print("running database_cleanup")
    users = bot.users

    # Grab all birthdays
    session: Session = db.Session()
    try:
        birthdays: List[db.Birthday] = session.query(db.Birthday).all()

        # Delete if birthday doesn't match an active user
        for birthday in birthdays:
            user_id = birthday.id
            user_present = False
            for user in users:
                if user_id == user.id:
                    user_present = True
                    break
            if not user_present:
                session.delete(birthday)

        session.commit()
        print("ran database_cleanup")
    except (SQLAlchemyError, OperationalError) as err:
        logger.error(err)
        session.rollback()
    finally:
        session.close()


async def birthday_message(bot: Bot):
    """Sends a daily birthday message for any birthdays"""

    print("running birthday_message")

    # Grab the Galaxy server
    guild: Guild = [guild for guild in bot.guilds if guild.id == GUILD_ID][0]

    # Initialize variables
    birthday_people = ""
    current_month = datetime.now().month
    current_day = datetime.now().day
    session: Session = db.Session()
    try:
        birthdays: List[db.Birthday] = session.query(db.Birthday).all()
    except (SQLAlchemyError, OperationalError) as err:
        logger.error(err)
    finally:
        session.close()

    # Loop through birthdays to find birthdays that match today's date
    for birthday in birthdays:
        member: Member = guild.get_member(int(birthday.id))

        if birthday.month == current_month and birthday.day == current_day:
            birthday_people += f"{member.mention}\n"

    # Send birthday message if there are any birthday people
    if birthday_people:
        channel: TextChannel = guild.system_channel
        announcement: Role = guild.get_role(GUILD_ANNOUCEMENT_ROLE_ID)

        embed = Embed(
            title="Happy Birthday!",
            description=f"""Please wish a happy birthday
             to the following {announcement.mention}!""",
        )
        embed.add_field(name="Users", value=birthday_people)
        embed.set_thumbnail(url="https://i.imgur.com/2LQPTEO.png")
        await channel.send(embed=embed)
    print("ran birthday_message")
