from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler


def test_get_files_in_folder_success(client: TestClient, db: Session, auth_handler: AuthHandler):
    """
    Testa a listagem de arquivos de uma pasta existente e pertencente ao usuário.
    """
    # Cria um usuário de teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword"
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Cria uma pasta de teste
    test_folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(test_folder)
    db.commit()

    # Cria arquivos na pasta de teste
    file_data = [
        {"filename": "file1.txt", "file_path": "/test_folder/file1.txt"},
        {"filename": "file2.txt", "file_path": "/test_folder/file2.txt"}
    ]
    for file in file_data:
        new_file = foldersModels.File(filename=file["filename"], file_path=file["file_path"], folder_id=test_folder.id, user_id=user.id)
        db.add(new_file)
    db.commit()

    user_email = db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()
    
    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Simula a requisição para listar os arquivos da pasta
    response = client.get(
        "/folders/test_folder/files/",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 200
    files = response.json()
    assert len(files) == 2
    assert files[0]["filename"] == "file1.txt"
    assert files[1]["filename"] == "file2.txt"


def test_get_files_in_folder_not_found(client: TestClient, db: Session, auth_handler: AuthHandler):
    """
    Testa a tentativa de listar arquivos de uma pasta inexistente.
    """
    # Cria um usuário de teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword"
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    user_email = db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()
    
    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Tenta listar arquivos de uma pasta inexistente
    response = client.get(
        "/folders/non_existent_folder/files/",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 403
    assert response.json()["detail"] == "Você não tem permissão para acessar esta pasta."


def test_get_files_in_folder_unauthenticated(client: TestClient):
    """
    Testa a tentativa de listar arquivos de uma pasta sem autenticação.
    """
    response = client.get("/folders/test_folder/files/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token não encontrado"
