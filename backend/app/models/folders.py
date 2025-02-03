from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from app.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"))

    user = relationship("User", back_populates="files")
    folder = relationship("Folder", back_populates="files") 


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False) 
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="folders")
    files = relationship("File", back_populates="folder")

    __table_args__ = (UniqueConstraint("path", "user_id", name="unique_user_folder"),) 