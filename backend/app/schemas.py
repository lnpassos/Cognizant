from pydantic import BaseModel
from datetime import datetime

# Esquema base para arquivos
class FileBase(BaseModel):
    filename: str

# Esquema para upload de arquivos
class FileCreate(FileBase):
    pass

# Esquema para resposta ao buscar arquivos
class FileResponse(FileBase):
    id: int
    file_path: str
    uploaded_at: datetime
    user_id: int

    class Config:
        orm_mode = True

# Schemas de usuário (mantendo os já definidos)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True

# Esquema para criação de pasta
class FolderCreate(BaseModel):
    folder_path: str  # Agora usamos `folder_path` para suportar subpastas

    class Config:
        orm_mode = True

# Esquema para resposta ao buscar pastas
class FolderResponse(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        orm_mode = True
