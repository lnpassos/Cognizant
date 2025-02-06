from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import users as models
from app.schemas import users as schemas
from app.services import users as services
from app.auth.jwt import AuthHandler  # Importando a classe AuthHandler

router = APIRouter()

# Instância da classe AuthHandler
auth_handler = AuthHandler()

# Registro de usuário
@router.post("/register/")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Valida o formato do email
    if not services.validate_email_format(user.email):
        raise HTTPException(status_code=400, detail="Email inválido")

    # Verifica se o email já está registrado (não permite emails duplicados)
    existing_user_by_email = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="Email já registrado")

    # Criptografa a senha
    hashed_password = services.get_password_hash(user.password)

    # Criação do objeto de usuário com email e senha
    user_obj = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    # Gera o token de acesso com o email (sub agora é o email)
    access_token = auth_handler.create_access_token(data={"sub": user_obj.email})

    # Prepara a resposta e define o token no cookie
    response = JSONResponse({"message": "Usuário criado com sucesso"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="Strict",
        secure=True,
        max_age=30 * 60,  # O token expira em 30 minutos
    )
    return response


# Função para login
@router.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Busca o usuário pelo email
    db_user = services.get_user_by_email(db, email=user.email)

    if not db_user or not services.verify_password(
        user.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # Geração do token usando o email
    access_token = auth_handler.create_access_token(data={"sub": db_user.email})

    response = JSONResponse({"message": "Login realizado com sucesso"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="Strict",
        secure=True,
        max_age=30 * 60,
    )

    return response


# Função para logout
@router.post("/logout/")
def logout():
    response = JSONResponse({"message": "Logout realizado com sucesso"})
    # Removendo o cookie corretamente
    response.delete_cookie("access_token", path="/", domain=None)

    return response


# Rota protegida (exemplo)
@router.get("/protected/")
def protected_route(request: Request, db: Session = Depends(get_db)):
    # Obtém o token dos cookies
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Token não encontrado")

    try:
        # Obtém o email do usuário a partir do token
        email = auth_handler.get_current_user(request)  # Método já busca nos cookies
        db_user = services.get_user_by_email(db, email=email)

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {"message": f"Bem-vindo, {db_user.username}!"}

    except Exception:
        # Captura exceções gerais (por exemplo, token inválido ou expirado)
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
