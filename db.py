"""
Database Related Code
"""


from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import get_config

config = get_config()

DATABASE_URI = config.get("DATABASE_URI")

Base = declarative_base()
engine = create_engine(DATABASE_URI)


class Birthday(Base):
    __tablename__ = "birthdays"

    id = Column("id", BigInteger, primary_key=True)
    username = Column("username", String(36), unique=True)
    month = Column("month", Integer)
    day = Column("day", Integer)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
