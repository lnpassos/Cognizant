import os
from app.models import users as usersModels, folders as foldersModels
from app.services.users import get_password_hash
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()

def test_create_folder(client, db):
    # Cria um usuário no banco de dados para teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword")  # Usa a função de services
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Gere o token JWT para o usuário usando create_access_token
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Define o cookie "access_token" no cliente
    client.cookies.set("access_token", token)

    # Dados para a criação da pasta
    folder_data = {
        "folder_path": "new_folder",  # Nome da nova pasta
    }

    # Chama a rota de criação da pasta
    response = client.post(
        "/create_folder/",
        data=folder_data
    )

    # Verifica se a resposta foi bem-sucedida
    assert response.status_code == 200
    assert response.json() == {"message": "Pasta criada com sucesso!"}

    # Verifica se a pasta foi criada no banco de dados
    folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.path == "new_folder").first()
    assert folder is not None
    assert folder.path == "new_folder"
    assert folder.user_id == user.id

    # Verifica se a pasta foi criada no diretório de uploads
    user_folder_path = os.path.join("uploads", user.email, "new_folder")
    assert os.path.exists(user_folder_path)

    # Limpeza: Remover a pasta criada após o teste (se estiver vazia)
    os.rmdir(user_folder_path)
