from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if TYPE_CHECKING:
    from logic.bot import Bot


BASE = declarative_base()


class DB:
    """DB class for the bot"""

    def __init__(self, bot: Bot):
        self.engine = create_engine(bot.config.get("DATABASE_URI"))
        self.session_maker = sessionmaker(bind=self.engine)
        BASE.metadata.create_all(bind=self.engine)


class Birthday(BASE):
    """Sqlalchemy class for birthday records"""

    __tablename__ = "birthdays"

    id = Column("id", BigInteger, primary_key=True)
    username = Column("username", String(36), unique=True)
    month = Column("month", Integer)
    day = Column("day", Integer)
