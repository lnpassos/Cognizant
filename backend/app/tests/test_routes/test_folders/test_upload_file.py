from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()

def test_upload_file_success(client: TestClient, db: Session, auth_handler: AuthHandler, test_file):
    """
    Testa o upload de um arquivo para uma pasta existente.
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

    user_email = db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()
    
    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Simula o upload de um arquivo
    response = client.post(
        "/upload/test_folder",
        files={"file": test_file},
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json()["message"] == "Arquivo enviado com sucesso"


def test_upload_file_folder_not_found(client: TestClient, db: Session, auth_handler: AuthHandler, test_file):
    """
    Testa a tentativa de upload de um arquivo para uma pasta inexistente.
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

    # Tenta enviar um arquivo para uma pasta que não existe
    response = client.post(
        "/upload/non_existent_folder",
        files={"file": test_file},
        cookies={"access_token": token}
    )

    # Verifica a resposta
    assert response.status_code == 404
    assert response.json()["detail"] == "Pasta não encontrada."


def test_upload_file_unauthenticated(client: TestClient, test_file):
    """
    Testa a tentativa de upload de um arquivo sem autenticação.
    """
    response = client.post(
        "/upload/test_folder",
        files={"file": test_file}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token não encontrado"
