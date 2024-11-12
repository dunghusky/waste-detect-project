from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connect_db._database_mysql import Base


class User(Base):
    __tablename__ = "User"

    maUser = Column(Integer, primary_key=True, autoincrement=True)
    userName = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
