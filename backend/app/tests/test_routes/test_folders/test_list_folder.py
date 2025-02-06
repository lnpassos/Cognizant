from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()

def test_list_folders(client, db, auth_handler):
    # Criação de um usuário de teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword"
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Gere um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Criação de algumas pastas associadas ao usuário
    folder1 = foldersModels.Folder(path="folder1", user_id=user.id)
    folder2 = foldersModels.Folder(path="folder2", user_id=user.id)
    db.add(folder1)
    db.add(folder2)
    db.commit()

    # Chama a rota para listar as pastas, incluindo o token no cookie de autenticação
    response = client.get(
        "/folders/",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica se a resposta foi bem-sucedida (status 200)
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2  # Espera duas pastas
    assert any(folder["path"] == "folder1" for folder in response_json)
    assert any(folder["path"] == "folder2" for folder in response_json)
