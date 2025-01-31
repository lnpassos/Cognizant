from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from typing import List

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
    files: List[UploadFile] = File(...),  # Altere para List[UploadFile]
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

        # Salva cada arquivo
        for file in files:
            file_path = os.path.join(full_folder_path, file.filename)
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            new_file = foldersModels.File(filename=file.filename, file_path=file_path, folder_id=folder.id)
            db.add(new_file)
            db.commit()

        return {"message": f"Pasta '{folder_path}' criada com sucesso e arquivos enviados!"}

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
        folder = db.query(foldersModels.Folder).filter(
            foldersModels.Folder.path == folder_name,
            foldersModels.Folder.user_id == db_user.id
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_path_full = os.path.join(UPLOAD_FOLDER, db_user.username, folder.path)
        os.makedirs(folder_path_full, exist_ok=True)

        # Verifica se já existe um arquivo com o mesmo nome e renomeia se necessário
        base_name, ext = os.path.splitext(file.filename)
        new_filename = file.filename
        counter = 1

        while os.path.exists(os.path.join(folder_path_full, new_filename)):
            new_filename = f"{base_name}({counter}){ext}"
            counter += 1

        file_path = os.path.join(folder_path_full, new_filename)
        
        # Salva o arquivo no sistema
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Salva no banco de dados
        new_file = foldersModels.File(
            filename=new_filename,
            file_path=file_path,
            user_id=db_user.id,
            folder_id=folder.id
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {"message": "Arquivo enviado com sucesso", "file": new_filename}

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


@router.delete("/delete_folder/{folder_path:path}")
def delete_folder(folder_path: str, db: Session = Depends(get_db), request: Request = None):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        # Remover os arquivos da pasta
        files = db.query(foldersModels.File).filter(foldersModels.File.folder_id == folder.id).all()
        for file in files:
            os.remove(file.file_path)  # Deletar o arquivo fisicamente
            db.delete(file)  # Remover o arquivo do banco de dados

        # Deletar a pasta do banco de dados
        db.delete(folder)
        db.commit()

        # Deletar a pasta fisicamente
        folder_full_path = os.path.join("uploads", db_user.username, folder_path)
        
        if os.path.exists(folder_full_path):
            shutil.rmtree(folder_full_path)  # Deletar a pasta e todo seu conteúdo (arquivos e subpastas)

        return {"message": f"Pasta '{folder_path}' e seus arquivos foram deletados com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/delete_file/{folder_path:path}/{filename}")
def delete_file(folder_path: str, filename: str, db: Session = Depends(get_db), request: Request = None):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.username == current_user).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        file_to_delete = db.query(foldersModels.File).filter(foldersModels.File.folder_id == folder.id, foldersModels.File.filename == filename).first()
        if not file_to_delete:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        # Corrigir caminho do arquivo para garantir que está sendo montado com o nome de usuário correto
        file_path = os.path.join("uploads", db_user.username, folder_path, filename)
        
        # Confirmação do caminho
        print(f"Deletando arquivo: {file_path}")
        
        # Deletar o arquivo fisicamente
        os.remove(file_path)
        
        # Remover o arquivo do banco de dados
        db.delete(file_to_delete)
        db.commit()

        return {"message": f"Arquivo '{filename}' deletado com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
