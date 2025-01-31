from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    folders = relationship("Folder", back_populates="user")
    files = relationship("File", back_populates="user")
