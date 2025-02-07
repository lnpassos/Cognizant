import os
import mimetypes
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, Request
import logging
from app.auth.jwt import AuthHandler
from app.models import users as usersModels
from app.models import folders as foldersModels
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
auth_handler = AuthHandler()
UPLOAD_FOLDER = "uploads"  # Path to store uploaded files


# Upload files
async def upload_user_file(
    folder_name: str, file: UploadFile, db: Session, request: Request
):
    current_user = auth_handler.get_current_user(request)

    # Verifying if the user is authenticated before any other action
    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    folder = (
        db.query(foldersModels.Folder)
        .filter(
            foldersModels.Folder.path == folder_name,
            foldersModels.Folder.user_id == db_user.id,
        )
        .first()
    )

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found.")

    # Creating the folder path
    folder_path_full = os.path.join(UPLOAD_FOLDER, db_user.email, folder.path)
    os.makedirs(folder_path_full, exist_ok=True)

    base_name, ext = os.path.splitext(file.filename)

    # Verifying if the file already exists
    existing_files = (
        db.query(foldersModels.File)
        .filter(
            foldersModels.File.folder_id == folder.id,
            foldersModels.File.filename.like(f"{base_name}_v%"),
        )
        .all()
    )

    # Defining the file name considering the version
    if existing_files:
        version_numbers = [
            int(f.filename.split("_v")[-1].split(".")[0]) for f in existing_files
        ]
        new_version = max(version_numbers) + 1
    else:
        new_version = 0

    # Defining the file path name
    new_filename = (
        f"{base_name}_v{new_version}{ext}" if new_version > 0 else f"{base_name}{ext}"
    )
    file_path = os.path.join(folder_path_full, new_filename)

    # Verifying if the file already exists, if so, increment the version
    while os.path.exists(file_path):
        new_version += 1
        new_filename = f"{base_name}_v{new_version}{ext}"
        file_path = os.path.join(folder_path_full, new_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    new_file = foldersModels.File(
        filename=new_filename,
        file_path=file_path,
        user_id=db_user.id,
        folder_id=folder.id,
        revision=new_version,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return {
        "message": "File uploaded successfully",
        "file": new_filename,
        "revision": new_version,
    }


# Get files
def get_files_from_folder(folder_path: str, db: Session, request: Request):
    current_user = auth_handler.get_current_user(request)

    # Verifying if the user is authenticated before any other action
    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    # Getting the folder
    folder = (
        db.query(foldersModels.Folder)
        .filter(
            foldersModels.Folder.path == folder_path,
            foldersModels.Folder.user_id == db_user.id,
        )
        .first()
    )

    if not folder:
        raise HTTPException(
            status_code=403, detail="You don't have permission to access this folder."
        )

    # Searching for files in the folder
    files = (
        db.query(foldersModels.File)
        .filter(foldersModels.File.folder_id == folder.id)
        .all()
    )

    return [
        {
            "id": file.id,
            "filename": file.filename,
            "file_path": file.file_path,
            "uploaded_at": file.uploaded_at,
            "revision": file.revision,
        }
        for file in files
    ]


# Delete file
def delete_file_from_path(
    folder_path: str, filename: str, db: Session, request: Request
):
    # Verify if the user is authenticated before any other action
    current_user = auth_handler.get_current_user(request)

    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    # Verify if the folder exists
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

    #  Verify if the file exists
    file_to_delete = (
        db.query(foldersModels.File)
        .filter(
            foldersModels.File.folder_id == folder.id,
            foldersModels.File.filename == filename,
        )
        .first()
    )
    if not file_to_delete:
        raise HTTPException(status_code=404, detail="File not found.")

    # Delete the file from the disk
    file_path = os.path.join("uploads", db_user.email, folder_path, filename)
    os.remove(file_path)

    # Delete the file from the database
    db.delete(file_to_delete)
    db.commit()

    return {"message": f"File '{filename}' successfully deleted!"}


# Download file
def download_file_from_path(folder_path: str, filename: str, db: Session, request):
    # Verify if the user is authenticated before any other action
    current_user = auth_handler.get_current_user(request)

    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    # Verify if the folder exists
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

    # Get the file
    folder_full_path = os.path.join("uploads", db_user.email, folder_path)
    file_path = os.path.join(folder_full_path, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(file_path, filename=filename)


# Preview file
def preview_file_from_path(
    folder_path: str, filename: str, review: int, db: Session, request
):
    # Verify if the user is authenticated before any other action
    current_user = auth_handler.get_current_user(request)

    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found.")

    # Verify if the folder exists
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

    # Get the file
    file_query = db.query(foldersModels.File).filter(
        foldersModels.File.folder_id == folder.id,
        foldersModels.File.filename.like(f"%{filename}%"),
    )

    if review is not None:
        file_query = file_query.filter(foldersModels.File.revision == review)

    file_record = file_query.first()
    folder_full_path = os.path.join("uploads", db_user.email, folder_path)
    file_path = os.path.join(folder_full_path, file_record.filename)

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    return FileResponse(file_path, media_type=mime_type)
