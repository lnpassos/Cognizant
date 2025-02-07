from fastapi import APIRouter, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import logging
import os
import shutil

from app.models import users as usersModels
from app.models import folders as foldersModels
from app.auth.jwt import AuthHandler

router = APIRouter()

# AuthHandler instance
auth_handler = AuthHandler()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger = logging.getLogger(__name__)


# Create a folder
def create_folder_service(
    folder_path: str, current_user: str, db: Session, files: List[UploadFile]
):
    # Checking the authenticated user in the database
    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    folder_path = folder_path.strip("/").lower()

    # Check if the folder already exists
    existing_folder = (
        db.query(foldersModels.Folder)
        .filter(
            func.lower(foldersModels.Folder.path) == folder_path,
            foldersModels.Folder.user_id == db_user.id,
        )
        .first()
    )

    if existing_folder:
        full_folder_path = os.path.join(
            UPLOAD_FOLDER, db_user.email, existing_folder.path
        )
    else:
        folder = foldersModels.Folder(path=folder_path, user_id=db_user.id)
        db.add(folder)
        db.commit()
        db.refresh(folder)
        full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
        os.makedirs(full_folder_path, exist_ok=True)

    # Handling file uploads
    for file in files:
        base_name, ext = os.path.splitext(file.filename)
        new_filename = file.filename

        # Check if there is already a file with the same base name
        existing_files = (
            db.query(foldersModels.File)
            .filter(
                foldersModels.File.folder_id
                == (existing_folder.id if existing_folder else folder.id),
                foldersModels.File.filename.like(f"{base_name}%"),
            )
            .all()
        )

        # If no file with the same base name exists, use the original name
        if not existing_files:
            new_filename = f"{base_name}{ext}"
            new_version = 0  # First file, no version suffix
        else:
            # If a file with the same base name exists, check if it's the first or if there are already versions
            if any(f.filename.startswith(f"{base_name}_v") for f in existing_files):
                version_numbers = [
                    int(f.filename.split("_v")[-1].split(".")[0])
                    for f in existing_files
                    if f.filename.startswith(f"{base_name}_v")
                ]
                new_version = max(version_numbers) + 1
            else:
                # If there are no versions with _v suffix, start with _v1
                new_version = 1

            new_filename = f"{base_name}_v{new_version}{ext}"

        # Check if the file already exists physically
        file_path = os.path.join(full_folder_path, new_filename)
        while os.path.exists(file_path):
            new_version += 1
            new_filename = f"{base_name}_v{new_version}{ext}"
            file_path = os.path.join(full_folder_path, new_filename)

        # Saving the file physically
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Save file details in the database
        new_file = foldersModels.File(
            filename=new_filename,
            file_path=file_path,
            folder_id=existing_folder.id if existing_folder else folder.id,
            user_id=db_user.id,
            revision=new_version,  # Storing the revision number
        )
        db.add(new_file)
        db.commit()

    return {
        "message": "Folder created successfully!"
        if not files
        else "Files uploaded successfully!"
    }


# List folders
def get_user_folders(db: Session, request: Request):
    # Get the authenticated user
    current_user = auth_handler.get_current_user(request)
    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Fetch user folders from the database
    folders = (
        db.query(foldersModels.Folder)
        .filter(foldersModels.Folder.user_id == db_user.id)
        .all()
    )

    # Return the formatted list
    return [
        {"id": folder.id, "path": folder.path, "name": folder.path.split("/")[-1]}
        for folder in folders
    ]


# Delete folder
def delete_folder_from_path(folder_path: str, db: Session, request: Request):
    # Check if the user is authenticated
    current_user = auth_handler.get_current_user(request)

    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    # Check if the folder exists
    folder = (
        db.query(foldersModels.Folder)
        .filter(
            foldersModels.Folder.path == folder_path,
            foldersModels.Folder.user_id == db_user.id,
        )
        .first()
    )

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found.")

    # Delete the files inside the folder
    files = (
        db.query(foldersModels.File)
        .filter(foldersModels.File.folder_id == folder.id)
        .all()
    )
    for file in files:
        if os.path.exists(file.file_path):  # Prevents error if the file does not exist
            os.remove(file.file_path)
        db.delete(file)

    # Remove the folder from the database
    db.delete(folder)
    db.commit()

    # Remove the folder from the file system
    folder_full_path = os.path.join(
        "uploads", db_user.email, os.path.normpath(folder_path)
    )
    if os.path.exists(folder_full_path):
        shutil.rmtree(folder_full_path)  # Removes the folder and all its contents

    return {
        "message": f"Folder '{folder_path}' and its files were successfully deleted!"
    }
