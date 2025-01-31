from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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
    folder = relationship("Folder", back_populates="files")  # Usando back_populates aqui


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)  # Agora armazenamos o caminho completo
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="folders")
    files = relationship("File", back_populates="folder")

