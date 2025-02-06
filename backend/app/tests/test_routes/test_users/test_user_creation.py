from app.models.users import User

# Teste para a rota de registro
def test_register(client, db, auth_handler):
    # Dados de teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }

    # Chama a rota de registro
    response = client.post("/register/", json=user_data)

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json() == {"message": "Usuário criado com sucesso"}

    # Verifica se o usuário foi criado no banco de dados
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.username == user_data["username"]

    # Verifica se o cookie de acesso foi definido
    assert "access_token" in response.cookies
