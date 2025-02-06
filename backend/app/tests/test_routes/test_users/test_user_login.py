from app.models.users import User
from app.services.users import get_password_hash

# Teste para a rota de login
def test_login(client, db):
    # Cria um usuário no banco de dados para teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword")  # Usa a função de services
    }
    user = User(**user_data)
    db.add(user)
    db.commit()

    # Dados de login
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }

    # Chama a rota de login
    response = client.post("/login/", json=login_data)

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json() == {"message": "Login realizado com sucesso"}

    # Verifica se o cookie de acesso foi definido
    assert "access_token" in response.cookies
