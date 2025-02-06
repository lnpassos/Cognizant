from app.models import users as usersModels
from app.services.users import get_password_hash
from app.auth.jwt import AuthHandler

auth_handler = AuthHandler()
UPLOAD_FOLDER = "uploads"

def test_home_authenticated(client, db):
    # Cria um usuário para o teste
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword")
    }
    user = usersModels.User(**user_data)
    db.add(user)
    db.commit()

    # Gera o token JWT para o usuário
    token = auth_handler.create_access_token(data={"sub": user.email})
    
    # Configura o cookie de autenticação
    client.cookies.set("access_token", token)

    # Faz uma requisição GET para a rota /home/
    response = client.get("/home/")

    # Verifica se o status code é 200
    assert response.status_code == 200