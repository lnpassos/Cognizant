from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import shutil
import mimetypes
from typing import List
import logging
from fastapi import Query

from app.db import get_db
from app.models import users as usersModels
from app.models import folders as foldersModels
from app.auth.jwt import AuthHandler

router = APIRouter()

# Instância da classe AuthHandler
auth_handler = AuthHandler()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger = logging.getLogger(__name__)


# Criar uma pasta
@router.post("/create_folder/")
def create_folder(
    folder_path: str = Form(...),
    db: Session = Depends(get_db),
    files: List[UploadFile] = File(default=[]),
    request: Request = None,
):
    try:
        # Verificando o usuário autenticado
        current_user = auth_handler.get_current_user(request)
        if not current_user:
            raise HTTPException(status_code=401, detail="Usuário não autenticado.")

        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")

        folder_path = folder_path.strip("/").lower()

        # Verificar se a pasta já existe
        existing_folder = db.query(foldersModels.Folder).filter(
            func.lower(foldersModels.Folder.path) == folder_path,
            foldersModels.Folder.user_id == db_user.id,
        ).first()

        if existing_folder:
            full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.email, existing_folder.path)
        else:
            folder = foldersModels.Folder(path=folder_path, user_id=db_user.id)
            db.add(folder)
            db.commit()
            db.refresh(folder)
            full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
            os.makedirs(full_folder_path, exist_ok=True)

        # Tratando os arquivos
        for file in files:
            base_name, ext = os.path.splitext(file.filename)
            new_filename = file.filename

            # Verifica se já existe algum arquivo com o mesmo nome base
            existing_files = db.query(foldersModels.File).filter(
                foldersModels.File.folder_id == (existing_folder.id if existing_folder else folder.id),
                foldersModels.File.filename.like(f"{base_name}%"),  # Busca por arquivos com o mesmo nome base
            ).all()

            # Se não houver arquivos com o mesmo nome base, usa o nome original (sem sufixo _v)
            if not existing_files:
                new_filename = f"{base_name}{ext}"
                new_version = 0  # Primeiro arquivo, sem sufixo de versão
            else:
                # Se já existir arquivo com o mesmo nome base, verifica se é o primeiro ou se já tem versões
                if any(f.filename.startswith(f"{base_name}_v") for f in existing_files):
                    # Extrai os números de versão dos arquivos existentes
                    version_numbers = [
                        int(f.filename.split("_v")[-1].split(".")[0])
                        for f in existing_files
                        if f.filename.startswith(f"{base_name}_v")
                    ]
                    new_version = max(version_numbers) + 1
                else:
                    # Se não houver versões com sufixo _v, começa com _v1
                    new_version = 1

                new_filename = f"{base_name}_v{new_version}{ext}"

            # Verifica se o arquivo já existe fisicamente
            file_path = os.path.join(full_folder_path, new_filename)
            while os.path.exists(file_path):
                new_version += 1
                new_filename = f"{base_name}_v{new_version}{ext}"
                file_path = os.path.join(full_folder_path, new_filename)

            # Salvando o arquivo fisicamente
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            # Salvar os detalhes do arquivo no banco de dados
            new_file = foldersModels.File(
                filename=new_filename,
                file_path=file_path,
                folder_id=existing_folder.id if existing_folder else folder.id,
                user_id=db_user.id,
                revision=new_version,  # Armazenando a revisão
            )
            db.add(new_file)
            db.commit()

        return {
            "message": "Pasta criada com sucesso!" if not files else "Arquivos enviados com sucesso!"
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Erro ao criar pasta: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao tentar criar a pasta.")


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

        # Verifica a quantidade de arquivos já existentes com o mesmo nome base
        existing_files = (
            db.query(foldersModels.File)
            .filter(
                foldersModels.File.folder_id == folder.id,
                foldersModels.File.filename.like(f"{base_name}_v%"),
            )
            .all()
        )

        # Se não houver arquivos com o sufixo _v, inicia com o nome base
        if existing_files:
            # A versão será baseada no maior número encontrado no sufixo _v
            version_numbers = [
                int(f.filename.split("_v")[-1].split(".")[0]) for f in existing_files
            ]
            new_version = max(version_numbers) + 1
        else:
            # Primeiro arquivo, sem sufixo
            new_version = 0

        # Atualiza o nome do arquivo com o novo sufixo de versão
        if new_version == 0:
            new_filename = f"{base_name}{ext}"  # Sem o sufixo "_v"
        else:
            new_filename = f"{base_name}_v{new_version}{ext}"

        # Verifica se o arquivo já existe para esse nome e versão
        file_path = os.path.join(folder_path_full, new_filename)
        while os.path.exists(file_path):
            new_version += 1
            if new_version == 0:
                new_filename = f"{base_name}{ext}"
            else:
                new_filename = f"{base_name}_v{new_version}{ext}"
            file_path = os.path.join(folder_path_full, new_filename)

        # Salva o arquivo no sistema de arquivos
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Adiciona o novo arquivo na base de dados
        new_file = foldersModels.File(
            filename=new_filename,
            file_path=file_path,
            user_id=db_user.id,
            folder_id=folder.id,
            revision=new_version,  # A revisão será o número da versão
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {"message": "Arquivo enviado com sucesso", "file": new_filename, "revision": new_version}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao fazer upload de arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail="Erro interno ao processar o upload.")


# Listar arquivos de uma pasta
@router.get("/folders/{folder_path:path}/files/")
def get_files_in_folder(
    folder_path: str, db: Session = Depends(get_db), request: Request = None
):
    try:
        current_user = auth_handler.get_current_user(request)
        db_user = db.query(usersModels.User).filter(usersModels.User.email == current_user).first()

        if not db_user:
            raise HTTPException(status_code=401, detail="Usuário não autenticado.")

        folder = db.query(foldersModels.Folder).filter(
            foldersModels.Folder.path == folder_path,
            foldersModels.Folder.user_id == db_user.id
        ).first()

        if not folder:
            raise HTTPException(status_code=403, detail="Você não tem permissão para acessar esta pasta.")

        files = db.query(foldersModels.File).filter(foldersModels.File.folder_id == folder.id).all()

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

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Erro inesperado ao buscar arquivos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")


# deletar uma pasta
@router.delete("/delete_folder/{folder_path:path}")
def delete_folder(
    folder_path: str, db: Session = Depends(get_db), request: Request = None
):
    # ✅ 1️⃣ Verifica a autenticação primeiro
    current_user = auth_handler.get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Usuário não autenticado.")

    # ✅ 2️⃣ Obtém o usuário autenticado no banco de dados
    db_user = (
        db.query(usersModels.User)
        .filter(usersModels.User.email == current_user)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # ✅ 3️⃣ Verifica se a pasta existe
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

    # ✅ 4️⃣ Obtém arquivos da pasta e deleta do banco
    files = (
        db.query(foldersModels.File)
        .filter(foldersModels.File.folder_id == folder.id)
        .all()
    )
    for file in files:
        if os.path.exists(file.file_path):  # Evita erro se o arquivo não existir
            os.remove(file.file_path)
        db.delete(file)

    # ✅ 5️⃣ Remove a pasta do banco e commit
    db.delete(folder)
    db.commit()

    # ✅ 6️⃣ Remove a pasta do sistema de arquivos
    folder_full_path = os.path.join("uploads", db_user.email, os.path.normpath(folder_path))
    
    if os.path.exists(folder_full_path):
        shutil.rmtree(folder_full_path)  # Remove a pasta e todo seu conteúdo

    return {
        "message": f"Pasta '{folder_path}' e seus arquivos foram deletados com sucesso!"
    }


# Deletar um arquivo
@router.delete("/delete_file/{folder_path:path}/{filename}")
def delete_file(
    folder_path: str,
    filename: str,
    db: Session = Depends(get_db),
    request: Request = None,
):
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
    
    try:
        os.remove(file_path)
        db.delete(file_to_delete)
        db.commit()
        return {"message": f"Arquivo '{filename}' deletado com sucesso!"}

    except Exception as e:
        logger.error(f"Erro ao deletar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao tentar deletar o arquivo.")


# Download de arquivo
@router.get("/download/{folder_path:path}/{filename}")
def download_file(
    folder_path: str, filename: str, request: Request, db: Session = Depends(get_db)
):
    try:
        # Obtém o usuário autenticado
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

    except HTTPException as http_error:
        raise http_error
    
    except Exception as e:
        logger.error(f"Erro ao fazer download de arquivo: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Visualização de arquivo
@router.get("/folders/{folder_path:path}/{filename}")
def preview_file(
    folder_path: str,
    filename: str,
    request: Request,
    db: Session = Depends(get_db),
    review: int = Query(None, description="Número da revisão do arquivo"),
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

        # Busca o arquivo no banco de dados com base no nome e na revisão
        file_query = db.query(foldersModels.File).filter(
            foldersModels.File.folder_id == folder.id,
            foldersModels.File.filename.like(f"%{filename}%"),
        )

        if review is not None:
            file_query = file_query.filter(foldersModels.File.revision == review)

        file_record = file_query.first()

        if not file_record:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.email, folder_path)
        file_path = os.path.join(folder_full_path, file_record.filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        return FileResponse(file_path, media_type=mime_type)

    except HTTPException as e:
        logger.error(f"Erro ao visualizar arquivo: {str(e.detail)}")
        raise e

    except Exception as e:
        logger.error(f"Erro inesperado ao visualizar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")