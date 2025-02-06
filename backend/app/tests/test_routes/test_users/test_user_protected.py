from app.models.users import User
from app.services.users import get_password_hash

# Teste para a rota protegida
def test_protected_route(client, db, auth_handler):
    # Cria um usuário de teste no banco de dados
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword")  # Função de hash
    }
    user = User(**user_data)
    db.add(user)
    db.commit()

    # Gera o token de acesso
    access_token = auth_handler.create_access_token(data={"sub": user.email})

    # Simula um cliente autenticado com o token armazenado no cookie
    client.cookies.set("access_token", access_token)

    # Chama a rota protegida
    response = client.get("/protected/")

    # Verifica se o acesso foi autorizado
    assert response.status_code == 200


# Teste para a rota protegida sem autenticação
def test_protected_route_unauthorized(client):
    # Chama a rota protegida sem token
    response = client.get("/protected/")

    # Verifica a resposta
    assert response.status_code == 401
    assert response.json() == {"detail": "Token não encontrado"}