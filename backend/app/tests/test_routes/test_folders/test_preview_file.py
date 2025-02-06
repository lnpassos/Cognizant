import os
from app.models import users as usersModels, folders as foldersModels
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()
UPLOAD_FOLDER = "uploads"

def test_preview_file_authenticated(client, db):
    # Criação de um usuário para o teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword"  # A senha já está hash
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Criação de uma pasta para o usuário
    folder = foldersModels.Folder(path="test_folder", user_id=user.id)
    db.add(folder)
    db.commit()

    # Adiciona um arquivo de exemplo à pasta (se possível)
    folder_full_path = os.path.join(UPLOAD_FOLDER, user.email, "test_folder")
    os.makedirs(folder_full_path, exist_ok=True)
    file_path = os.path.join(folder_full_path, "testfile.txt")
    with open(file_path, "w") as f:
        f.write("Conteúdo do arquivo de teste")

    # Gere um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Define o cookie "access_token" no cliente
    client.cookies.set("access_token", token)

    # Faz uma requisição GET para a rota de visualização do arquivo
    response = client.get(
        "/preview/test_folder/testfile.txt",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica se a resposta foi bem-sucedida (status 200)
    assert response.status_code == 200

    # Removendo a parte charset=utf-8 da comparação do tipo MIME
    content_type = response.headers["Content-Type"].split(";")[0]
    assert content_type == "text/plain"  # Verifica o tipo MIME sem o charset

    # Decodificando o conteúdo da resposta em bytes para string e comparando
    assert response.content.decode("utf-8") == "Conteúdo do arquivo de teste"

    # Limpeza: Remover o arquivo e a pasta criados após o teste
    os.remove(file_path)
    os.rmdir(folder_full_path)
    db.delete(folder)
    db.commit()



def test_preview_file_not_found(client, db):
    # Criação de um usuário para o teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword"
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Criação da pasta no banco de dados para evitar erro "Pasta não encontrada"
    folder_data = {
        "path": "test_folder",  # Corrigido: Removido "name", pois não existe no modelo
        "user_id": user.id
    }
    folder = foldersModels.Folder(**folder_data)
    db.add(folder)
    db.commit()

    # Gere um token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user.email})

    # Define o cookie "access_token" no cliente
    client.cookies.set("access_token", token)

    # Tenta acessar um arquivo que não existe dentro da pasta existente
    response = client.get(
        "/preview/test_folder/nonexistentfile.txt",
        cookies={"access_token": token}  # Envia o token como cookie
    )

    # Verifica se o status code é 404 (Arquivo não encontrado)
    assert response.status_code == 404
    assert response.json() == {"detail": "Arquivo não encontrado."}