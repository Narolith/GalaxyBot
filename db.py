"""
Database Related Code
"""


from dotenv import dotenv_values
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load configuration from .env
config = dotenv_values(".env")

DATABASE_URI = config.get("DATABASE_URI")

Base = declarative_base()
engine = create_engine(DATABASE_URI)


class Birthday(Base):
    __tablename__ = "birthday"

    id = Column("id", BigInteger, primary_key=True)
    username = Column("username", String(36), unique=True)
    month = Column("month", Integer)
    day = Column("day", Integer)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
