from pydantic import BaseModel
from datetime import datetime


class FileCreate(BaseModel):
    filename: str


class FileResponse(FileCreate):
    id: int
    file_path: str
    uploaded_at: datetime
    user_id: int

    class Config:
        orm_mode = True


class FolderCreate(BaseModel):
    folder_path: str

    class Config:
        orm_mode = True


class FolderResponse(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        orm_mode = True
