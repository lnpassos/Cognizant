import os
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()

def test_delete_folder_success(client, db, auth_handler):
    """
    Testa a exclusão de uma pasta com sucesso.
    Verifica se a pasta e seus arquivos são removidos do banco de dados e do sistema de arquivos.
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

    # Cria um arquivo de teste na pasta
    test_file = foldersModels.File(
        filename="test_file.txt",
        file_path=os.path.join("uploads", user.email, "test_folder", "test_file.txt"),
        user_id=user.id,
        folder_id=test_folder.id
    )
    db.add(test_file)
    db.commit()

    # Cria a pasta e o arquivo no sistema de arquivos
    folder_full_path = os.path.join("uploads", user.email, "test_folder")
    os.makedirs(folder_full_path, exist_ok=True)
    with open(os.path.join(folder_full_path, "test_file.txt"), "w") as f:
        f.write("Test file content")

    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Faz a requisição para deletar a pasta
    response = client.delete(
        "/delete_folder/test_folder",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json()["message"] == "Pasta 'test_folder' e seus arquivos foram deletados com sucesso!"

    # Verifica se a pasta foi removida do banco de dados
    deleted_folder = db.query(foldersModels.Folder).filter(foldersModels.Folder.id == test_folder.id).first()
    assert deleted_folder is None

    # Verifica se o arquivo foi removido do banco de dados
    deleted_file = db.query(foldersModels.File).filter(foldersModels.File.id == test_file.id).first()
    assert deleted_file is None

    # Verifica se a pasta foi removida do sistema de arquivos
    assert not os.path.exists(folder_full_path)


def test_delete_folder_not_found(client, db, auth_handler):
    """
    Testa a tentativa de exclusão de uma pasta que não existe.
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

    # Gera um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Faz a requisição para deletar uma pasta que não existe
    response = client.delete(
        "/delete_folder/nonexistent_folder",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica a resposta
    assert response.status_code == 404
    assert response.json()["detail"] == "Pasta não encontrada."
