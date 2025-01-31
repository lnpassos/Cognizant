from pydantic import BaseModel
from datetime import datetime

# Esquema para upload de arquivos
class FileCreate(BaseModel):
    filename: str

# Esquema para resposta ao buscar arquivos
class FileResponse(FileCreate):
    id: int
    file_path: str
    uploaded_at: datetime
    user_id: int

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
