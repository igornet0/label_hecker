from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from . import db

session = Session(db)
Base = declarative_base()

class Dataset(Base):
    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    files_count = Column(Integer)
    error_count = Column(Integer)

    def __init__(self, path, files_count, error_count):
        self.path = path
        self.files_count = files_count
        self.error_count = error_count
        if not session.query(Dataset).filter(Dataset.path == path).first():
            session.add(self)
            session.commit()
        else:
            self = session.query(Dataset).filter(Dataset.path == path).first()
            self.set_error_count(error_count)
            self.set_files_count(files_count)

    def set_files_count(self, files_count):
        self.files_count = files_count
        session.commit()

    def set_error_count(self, error_count):
        self.error_count = error_count
        session.commit()

Base.metadata.create_all(db)