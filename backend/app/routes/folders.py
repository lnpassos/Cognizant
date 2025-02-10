from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi import Query
from app.db import get_db
from app.auth.jwt import AuthHandler
import os

# Services
from app.services.folders import (
    create_folder_service,
    get_user_folders,
    delete_folder_from_path,
)
from app.services.files import (
    upload_user_file,
    get_files_from_folder,
    delete_file_from_path,
    download_file_from_path,
    preview_file_from_path,
)

router = APIRouter()

# AuthHandler instance
auth_handler = AuthHandler()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Create a folder
@router.post("/create_folder/")
def create_folder(
    folder_path: str = Form(...),
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(default=[]),
    request: Request = None,
):
    current_user = auth_handler.get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated.")

    return create_folder_service(folder_path, current_user, db, files)


# List user folders
@router.get("/folders/")
def list_folders(db: Session = Depends(get_db), request: Request = None):
    return get_user_folders(db, request)


# Upload a file
@router.post("/upload/{folder_name:path}")
async def upload_file(
    folder_name: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    request: Request = None,
):
    return await upload_user_file(folder_name, file, db, request)


# List files in a folder
@router.get("/folder/{folder_path:path}/files/")
def get_files_in_folder(
    folder_path: str, db: Session = Depends(get_db), request: Request = None
):
    return get_files_from_folder(folder_path, db, request)


# Delete a folder
@router.delete("/delete_folder/{folder_path:path}")
def delete_folder(
    folder_path: str, db: Session = Depends(get_db), request: Request = None
):
    return delete_folder_from_path(folder_path, db, request)


# Delete a file
@router.delete("/delete_file/{folder_path:path}/{filename}")
def delete_file(
    folder_path: str,
    filename: str,
    db: Session = Depends(get_db),
    request: Request = None,
):
    return delete_file_from_path(folder_path, filename, db, request)


# Download a file
@router.get("/download/{folder_path:path}/{filename}")
def download_file(
    folder_path: str,
    filename: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return download_file_from_path(folder_path, filename, db, request)


# Preview a file
@router.get("/folder/{folder_path:path}/{filename}")
def preview_file(
    folder_path: str,
    filename: str,
    request: Request,
    db: Session = Depends(get_db),
    review: int = Query(None, description="File revision number"),
):
    return preview_file_from_path(folder_path, filename, review, db, request)
