from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import shutil
import mimetypes
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


def get_unique_filename(folder_path, filename):
    base_name, ext = os.path.splitext(filename)
    new_filename = filename
    counter = 1

    # Verifica se o arquivo já existe, e caso sim, adiciona um contador ao nome
    while os.path.exists(os.path.join(folder_path, new_filename)):
        new_filename = f"{base_name}({counter}){ext}"
        counter += 1

    return new_filename

# Criar uma pasta
@router.post("/create_folder/")
def create_folder(
    folder_path: str = Form(...),
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(default=[]),  # Ajuste: agora o 'files' é uma lista vazia por padrão
    request: Request = None
):
    try:
        # Obtendo o usuário atual
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Normalizando o caminho da pasta para minúsculas
        folder_path = folder_path.strip("/").lower()

        # Verifica se já existe uma pasta com o mesmo nome (insensível a maiúsculas/minúsculas)
        existing_folder = db.query(foldersModels.Folder).filter(
                func.lower(foldersModels.Folder.path) == folder_path,  # Usa func.lower() para comparação insensível a maiúsculas
                foldersModels.Folder.user_id == db_user.id
            ).first()

        # Se a pasta já existe, usa o caminho completo da pasta existente
        if existing_folder:
            full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.email, existing_folder.path)
        else:
            # Cria uma nova pasta
            folder = foldersModels.Folder(path=folder_path, user_id=db_user.id)
            db.add(folder)
            db.commit()
            db.refresh(folder)

            full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
            os.makedirs(full_folder_path, exist_ok=True)

        # Se houver arquivos, salve-os
        for file in files:
            base_name, ext = os.path.splitext(file.filename)
            new_filename = file.filename

            # Verifica se já existe um arquivo com o mesmo nome e renomeia se necessário
            while os.path.exists(os.path.join(full_folder_path, new_filename)):
                if "(v" in new_filename:
                    base_name, ext = os.path.splitext(file.filename)
                    version_number = int(new_filename.split("(v")[-1].split(")")[0]) + 1
                    new_filename = f"{base_name}(v{version_number}){ext}"
                else:
                    new_filename = f"{base_name}(v1){ext}"

            file_path = os.path.join(full_folder_path, new_filename)

            # Salva o arquivo no sistema
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            # Adiciona o arquivo ao banco de dados
            new_file = foldersModels.File(
                filename=new_filename,
                file_path=file_path,
                folder_id=existing_folder.id if existing_folder else folder.id,
                user_id=db_user.id
            )
            db.add(new_file)
            db.commit()

        return {"message": "Pasta criada com sucesso!" if not files else "Arquivos enviados com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Listar pastas do usuário
@router.get("/folders/")
def get_folders(db: Session = Depends(get_db), request: Request = None):
    try:
        # Obtém o usuário atual a partir do JWT
        current_user = jwt.get_current_user(request)
        
        # Busca o usuário no banco de dados
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

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
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Filtro de pasta corrigido
        folder = db.query(foldersModels.Folder).filter(
            foldersModels.Folder.path == folder_name,
            foldersModels.Folder.user_id == db_user.id
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_path_full = os.path.join(UPLOAD_FOLDER, db_user.email, folder.path)
        os.makedirs(folder_path_full, exist_ok=True)

        # Verifica se já existe um arquivo com o mesmo nome e renomeia se necessário
        base_name, ext = os.path.splitext(file.filename)
        new_filename = file.filename

        # Verifica se já existe um arquivo com o nome base no diretório
        while os.path.exists(os.path.join(folder_path_full, new_filename)):
            # Verifica a versão do arquivo
            if "(v" in new_filename:
                base_name, ext = os.path.splitext(file.filename)
                # Encontra o número da versão atual
                version_number = int(new_filename.split("(v")[-1].split(")")[0]) + 1
                new_filename = f"{base_name}(v{version_number}){ext}"
            else:
                new_filename = f"{base_name}(v1){ext}"

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


# Listar arquivos de uma pasta
@router.get("/folders/{folder_path:path}/files/")
def get_files_in_folder(folder_path: str, db: Session = Depends(get_db), request: Request = None):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

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
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

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

        # Limpar o caminho para evitar problemas com barras extras
        folder_path_clean = os.path.normpath(folder_path)  # Isso ajuda a garantir que o caminho seja bem formado
        folder_full_path = os.path.join("uploads", db_user.email, folder_path_clean)

        # Verificar o caminho completo para debug
        print("Tentando deletar o diretório:", folder_full_path)

        # Deletar a pasta fisicamente
        if os.path.exists(folder_full_path):
            print(f"Deletando diretório: {folder_full_path}")
            shutil.rmtree(folder_full_path)  # Deleta o diretório e tudo dentro dele
        else:
            print(f"Diretório {folder_full_path} não encontrado.")

        # Agora, percorremos os diretórios para verificar se algum pai ficou vazio
        # Exemplo: Se você deleta `leo`, o caminho `downloads/pdf` pode ficar vazio
        parent_dir = os.path.dirname(folder_full_path)  # Diretório pai de 'leo'
        while os.path.isdir(parent_dir) and len(os.listdir(parent_dir)) == 0:
            print(f"Deletando diretório vazio: {parent_dir}")
            os.rmdir(parent_dir)  # Remover o diretório vazio
            parent_dir = os.path.dirname(parent_dir)  # Subir para o diretório pai

        return {"message": f"Pasta '{folder_path}' e seus arquivos foram deletados com sucesso!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_file/{folder_path:path}/{filename}")
def delete_file(folder_path: str, filename: str, db: Session = Depends(get_db), request: Request = None):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        file_to_delete = db.query(foldersModels.File).filter(foldersModels.File.folder_id == folder.id, foldersModels.File.filename == filename).first()
        if not file_to_delete:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        # Corrigir caminho do arquivo para garantir que está sendo montado com o nome de usuário correto
        file_path = os.path.join("uploads", db_user.email, folder_path, filename)
        
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


# Download de arquivo
@router.get("/download/{folder_path:path}/{filename}")
def download_file(folder_path: str, filename: str, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == folder_path, foldersModels.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
        file_path = os.path.join(folder_full_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        return FileResponse(file_path, filename=filename)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/preview/{folder_path:path}/{filename}")
def preview_file(
    folder_path: str,
    filename: str,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Obtém o usuário autenticado pelo token JWT
        current_user = jwt.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Verifica se a pasta pertence ao usuário
        folder = db.query(foldersModels.Folder).filter(
            foldersModels.Folder.path == folder_path, 
            foldersModels.Folder.user_id == db_user.id
        ).first()

        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        # Caminho do arquivo dentro da pasta do usuário
        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
        file_path = os.path.join(folder_full_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        # Determina o tipo MIME do arquivo para exibição correta
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Tipo padrão se não identificado

        # Retorna o arquivo com o tipo MIME correto para visualização no navegador
        return FileResponse(file_path, media_type=mime_type)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    