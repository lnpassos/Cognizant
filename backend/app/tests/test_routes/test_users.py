from app.models.users import User
from app.services.users import get_password_hash

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


# Teste para a rota de logout
def test_logout(client):
    # Chama a rota de logout
    response = client.post("/logout/")

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json() == {"message": "Logout realizado com sucesso"}

    # Verifica se o cookie de acesso foi removido
    assert "access_token" not in response.cookies

# Teste para a rota protegida
def test_protected_route(client, db, auth_handler):
    # Cria um usuário no banco de dados para teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword")  # Use a função de services
    }
    user = User(**user_data)
    db.add(user)
    db.commit()

    # Gera um token de acesso
    access_token = auth_handler.create_access_token(data={"sub": user.email})

    # Chama a rota protegida com o token no cabeçalho
    response = client.get(
        "/protected/",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Verifica a resposta
    assert response.status_code == 200
    assert response.json() == {"message": f"Bem-vindo, {user.username}!"}


# Teste para a rota protegida sem autenticação
def test_protected_route_unauthorized(client):
    # Chama a rota protegida sem token
    response = client.get("/protected/")

    # Verifica a resposta
    assert response.status_code == 401
    assert response.json() == {"detail": "Token não encontrado"}