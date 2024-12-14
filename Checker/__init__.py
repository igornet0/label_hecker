from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

db = create_engine("sqlite:///Checker.db")
session = sessionmaker(bind=db)

from .checker import Checker
from .model import *

__all__ = ["Checker"]