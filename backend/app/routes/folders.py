from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.db import get_db
from app.models import users as usersModels
from app.models import folders as foldersModels
from app.auth import jwt

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.get("/home/")
def home(request: Request):
    try:
        current_user = jwt.get_current_user(request)
        return {"message": f"Bem-vindo, {current_user}!"}
    except Exception:
        raise HTTPException(status_code=401, detail="Sessão expirada, faça login novamente")

# Criar uma pasta
@router.post("/create_folder/")
def create_folder(
    folder_path: str = Form(...),  
    db: Session = Depends(get_db), 
    file: UploadFile = File(None),
    request: Request = None
):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder_path = folder_path.strip("/")  
        existing_folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()

        if existing_folder:
            raise HTTPException(status_code=400, detail="Pasta já existe.")

        folder = foldersModels.Folder(path=folder_path, user_id=db_user.id)
        db.add(folder)
        db.commit()
        db.refresh(folder)

        full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_path)
        os.makedirs(full_folder_path, exist_ok=True)

        if file:
            file_path = os.path.join(full_folder_path, file.filename)
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            new_file = foldersModels.File(filename=file.filename, file_path=file_path, folder_id=folder.id)
            db.add(new_file)
            db.commit()

        return {"message": f"Pasta '{folder_path}' criada com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Listar pastas do usuário
@router.get("/folders/")
def get_folders(db: Session = Depends(get_db), request: Request = None):
    try:
        # Obtém o usuário atual a partir do JWT
        current_user = jwt.get_current_user(request)
        
        # Busca o usuário no banco de dados
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Busca as pastas do usuário no banco de dados
        folders = db.query(foldersModels.Folder).filter(foldersModels.Folder.user_id == db_user.id).all()

        # Retorna as pastas com o ID, caminho e nome
        return [{"id": folder.id, "path": folder.path, "name": folder.path.split("/")[-1]} for folder in folders]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Upload de arquivo para uma pasta
@router.post("/upload/{folder_name:path}")
async def upload_file(
    folder_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    request: Request = None
):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Filtro de pasta corrigido
        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_name, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_path_full = os.path.join(UPLOAD_FOLDER, db_user.username, folder.path)
        os.makedirs(folder_path_full, exist_ok=True)

        file_path = os.path.join(folder_path_full, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        new_file = foldersModels.File(
            filename=file.filename,
            file_path=file_path,
            user_id=db_user.id,
            folder_id=folder.id
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {"message": "Arquivo enviado com sucesso", "file": new_file.filename}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Download de arquivo
@router.get("/download/{folder_path:path}/{filename}")
def download_file(folder_path: str, filename: str, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_path)
        file_path = os.path.join(folder_full_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        return FileResponse(file_path, filename=filename)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Listar arquivos de uma pasta
@router.get("/folders/{folder_path:path}/files/")
def get_files_in_folder(folder_path: str, db: Session = Depends(get_db), request: Request = None):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        files = db.query(foldersModels.File).filter(foldersModels.File.folder_id == folder.id).all()

        return [{"id": file.id, "filename": file.filename, "file_path": file.file_path, "uploaded_at": file.uploaded_at} for file in files]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
