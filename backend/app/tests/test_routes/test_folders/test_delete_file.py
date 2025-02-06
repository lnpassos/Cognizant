import os
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()

def test_delete_file_success(client, db, auth_handler):
    """
    Testa a exclusão de um arquivo com sucesso.
    Verifica se o arquivo é removido do banco de dados e do sistema de arquivos.
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

    # Cria uma pasta de teste para o usuário
    test_folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(test_folder)
    db.commit()

    user_email = db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()

    # Cria um arquivo de teste na pasta
    test_file = foldersModels.File(
        filename="test_file.txt",
        file_path=os.path.join("uploads", user_email, "test_folder", "test_file.txt"),
        user_id=user.id,
        folder_id=test_folder.id
    )
    db.add(test_file)
    db.commit()

    # Cria a pasta e o arquivo no sistema de arquivos
    folder_full_path = os.path.join("uploads", user_email, "test_folder")
    os.makedirs(folder_full_path, exist_ok=True)
    with open(os.path.join(folder_full_path, "test_file.txt"), "w") as f:
        f.write("Test file content")

    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Faz a requisição para deletar o arquivo
    response = client.delete(
        "/delete_file/test_folder/test_file.txt",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json()["message"] == "Arquivo 'test_file.txt' deletado com sucesso!"

    # Verifica se o arquivo foi removido do banco de dados
    deleted_file = db.query(foldersModels.File).filter(foldersModels.File.id == test_file.id).first()
    assert deleted_file is None

    # Verifica se o arquivo foi removido do sistema de arquivos
    file_path = os.path.join("uploads", user_email, "test_folder", "test_file.txt")
    assert not os.path.exists(file_path)


def test_delete_file_not_found(client, db, auth_handler):
    """
    Testa a tentativa de exclusão de um arquivo que não existe.
    Verifica se o endpoint retorna um erro 404.
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

    # Cria uma pasta de teste para o usuário
    test_folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(test_folder)
    db.commit()

    user_email = db.query(usersModels.User.email).filter(usersModels.User.id == user.id).scalar()

    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user_email})

    # Faz a requisição para deletar um arquivo que não existe
    response = client.delete(
        "/delete_file/test_folder/nonexistent_file.txt",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 404
    assert response.json()["detail"] == "Arquivo não encontrado."


def test_delete_file_unauthenticated(client):
    """
    Testa a tentativa de exclusão de um arquivo sem autenticação.
    Verifica se o endpoint retorna um erro 401.
    """
    # Faz a requisição sem token de autenticação
    response = client.delete(
        "/delete_file/test_folder/test_file.txt"
    )

    # Verifica a resposta
    assert response.status_code == 401
    assert response.json()["detail"] == "Token não encontrado"