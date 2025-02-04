from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import shutil
import mimetypes
from typing import List
import logging

from app.db import get_db
from app.models import users as usersModels
from app.models import folders as foldersModels
from app.auth.jwt import AuthHandler  # Importando a classe AuthHandler

router = APIRouter()

# Instância da classe AuthHandler
auth_handler = AuthHandler()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger = logging.getLogger(__name__)


# Rota de boas-vindas
@router.get("/home/")
def home(request: Request):
    try:
        current_user = auth_handler.get_current_user(request)
        return {"message": f"Bem-vindo, {current_user}!"}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=401, detail="Sessão expirada, faça login novamente"
        )


# Função auxiliar para gerar nomes de arquivos únicos
def get_unique_filename(folder_path, filename):
    base_name, ext = os.path.splitext(filename)
    new_filename = filename
    counter = 1

    while os.path.exists(os.path.join(folder_path, new_filename)):
        new_filename = f"{base_name}({counter}){ext}"
        counter += 1

    return new_filename


# Criar uma pasta
@router.post("/create_folder/")
def create_folder(
    folder_path: str = Form(...),
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(default=[]),
    request: Request = None,
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder_path = folder_path.strip("/").lower()

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

        for file in files:
            base_name, ext = os.path.splitext(file.filename)
            new_filename = file.filename

            while os.path.exists(os.path.join(full_folder_path, new_filename)):
                if "(v" in new_filename:
                    base_name, ext = os.path.splitext(file.filename)
                    version_number = int(new_filename.split("(v")[-1].split(")")[0]) + 1
                    new_filename = f"{base_name}(v{version_number}){ext}"
                else:
                    new_filename = f"{base_name}(v1){ext}"

            file_path = os.path.join(full_folder_path, new_filename)

            with open(file_path, "wb") as f:
                f.write(file.file.read())

            new_file = foldersModels.File(
                filename=new_filename,
                file_path=file_path,
                folder_id=existing_folder.id if existing_folder else folder.id,
                user_id=db_user.id,
            )
            db.add(new_file)
            db.commit()

        return {
            "message": "Pasta criada com sucesso!"
            if not files
            else "Arquivos enviados com sucesso!"
        }

    except Exception as e:
        logger.error(f"Erro ao criar pasta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Listar pastas do usuário
@router.get("/folders/")
def get_folders(db: Session = Depends(get_db), request: Request = None):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folders = (
            db.query(foldersModels.Folder)
            .filter(foldersModels.Folder.user_id == db_user.id)
            .all()
        )

        return [
            {"id": folder.id, "path": folder.path, "name": folder.path.split("/")[-1]}
            for folder in folders
        ]

    except Exception as e:
        logger.error(f"Erro ao listar pastas: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Upload de arquivo para uma pasta
@router.post("/upload/{folder_name:path}")
async def upload_file(
    folder_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None,
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = (
            db.query(foldersModels.Folder)
            .filter(
                foldersModels.Folder.path == folder_name,
                foldersModels.Folder.user_id == db_user.id,
            )
            .first()
        )
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_path_full = os.path.join(UPLOAD_FOLDER, db_user.email, folder.path)
        os.makedirs(folder_path_full, exist_ok=True)

        base_name, ext = os.path.splitext(file.filename)
        new_filename = file.filename

        while os.path.exists(os.path.join(folder_path_full, new_filename)):
            if "(v" in new_filename:
                base_name, ext = os.path.splitext(file.filename)
                version_number = int(new_filename.split("(v")[-1].split(")")[0]) + 1
                new_filename = f"{base_name}(v{version_number}){ext}"
            else:
                new_filename = f"{base_name}(v1){ext}"

        file_path = os.path.join(folder_path_full, new_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        new_file = foldersModels.File(
            filename=new_filename,
            file_path=file_path,
            user_id=db_user.id,
            folder_id=folder.id,
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {"message": "Arquivo enviado com sucesso", "file": new_filename}

    except Exception as e:
        logger.error(f"Erro ao fazer upload de arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Listar arquivos de uma pasta
@router.get("/folders/{folder_path:path}/files/")
def get_files_in_folder(
    folder_path: str, db: Session = Depends(get_db), request: Request = None
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=401, detail="Usuário não autenticado.")

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
                status_code=403,
                detail="Você não tem permissão para acessar esta pasta.",
            )

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
            }
            for file in files
        ]

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar arquivos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


# Deletar uma pasta
@router.delete("/delete_folder/{folder_path:path}")
def delete_folder(
    folder_path: str, db: Session = Depends(get_db), request: Request = None
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = (
            db.query(foldersModels.Folder)
            .filter(
                foldersModels.Folder.path == folder_path,
                foldersModels.Folder.user_id == db_user.id,
            )
            .first()
        )
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        files = (
            db.query(foldersModels.File)
            .filter(foldersModels.File.folder_id == folder.id)
            .all()
        )
        for file in files:
            os.remove(file.file_path)
            db.delete(file)

        db.delete(folder)
        db.commit()

        folder_path_clean = os.path.normpath(folder_path)
        folder_full_path = os.path.join("uploads", db_user.email, folder_path_clean)

        if os.path.exists(folder_full_path):
            shutil.rmtree(folder_full_path)

        parent_dir = os.path.dirname(folder_full_path)
        while os.path.isdir(parent_dir) and len(os.listdir(parent_dir)) == 0:
            os.rmdir(parent_dir)
            parent_dir = os.path.dirname(parent_dir)

        return {
            "message": f"Pasta '{folder_path}' e seus arquivos foram deletados com sucesso!"
        }

    except Exception as e:
        logger.error(f"Erro ao deletar pasta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Deletar um arquivo
@router.delete("/delete_file/{folder_path:path}/{filename}")
def delete_file(
    folder_path: str,
    filename: str,
    db: Session = Depends(get_db),
    request: Request = None,
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = (
            db.query(foldersModels.Folder)
            .filter(
                foldersModels.Folder.path == folder_path,
                foldersModels.Folder.user_id == db_user.id,
            )
            .first()
        )
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        file_to_delete = (
            db.query(foldersModels.File)
            .filter(
                foldersModels.File.folder_id == folder.id,
                foldersModels.File.filename == filename,
            )
            .first()
        )
        if not file_to_delete:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        file_path = os.path.join("uploads", db_user.email, folder_path, filename)
        os.remove(file_path)

        db.delete(file_to_delete)
        db.commit()

        return {"message": f"Arquivo '{filename}' deletado com sucesso!"}

    except Exception as e:
        logger.error(f"Erro ao deletar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Download de arquivo
@router.get("/download/{folder_path:path}/{filename}")
def download_file(
    folder_path: str, filename: str, request: Request, db: Session = Depends(get_db)
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = (
            db.query(foldersModels.Folder)
            .filter(
                foldersModels.Folder.path == folder_path,
                foldersModels.Folder.user_id == db_user.id,
            )
            .first()
        )
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
        file_path = os.path.join(folder_full_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        return FileResponse(file_path, filename=filename)

    except Exception as e:
        logger.error(f"Erro ao fazer download de arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Visualizar arquivo
@router.get("/preview/{folder_path:path}/{filename}")
def preview_file(
    folder_path: str, filename: str, request: Request, db: Session = Depends(get_db)
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = (
            db.query(usersModels.User)
            .filter(usersModels.User.email == current_user)
            .first()
        )

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = (
            db.query(foldersModels.Folder)
            .filter(
                foldersModels.Folder.path == folder_path,
                foldersModels.Folder.user_id == db_user.id,
            )
            .first()
        )
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
        file_path = os.path.join(folder_full_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        return FileResponse(file_path, media_type=mime_type)

    except Exception as e:
        logger.error(f"Erro ao visualizar arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
