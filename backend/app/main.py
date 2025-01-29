from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, services, db
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
from fastapi import Request

# Determina se está rodando em ambiente de produção ou desenvolvimento
IS_PRODUCTION = os.getenv("ENV") == "production"

# Configuração JWT
class Settings(BaseModel):
    authjwt_secret_key: str = "your_secret_key"  # Substitua por uma chave forte

@AuthJWT.load_config
def get_config():
    return Settings()

# Configuração FastAPI
app = FastAPI()

# Configuração CORS
origins = [
    "http://localhost:3000",
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criação das tabelas do banco de dados
models.Base.metadata.create_all(bind=db.engine)

# Função para gerar um token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None, Authorize: AuthJWT = Depends()):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    return Authorize.create_access_token(subject=data['username'], expires_time=expire)

# Função para verificar o token no backend
@app.get("/home/")
def home(request: Request, Authorize: AuthJWT = Depends()):
    try:
        access_token = request.cookies.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Token não encontrado")

        Authorize._token = access_token 
        Authorize.jwt_required() 

        current_user = Authorize.get_jwt_subject()
        return {"message": f"Bem-vindo, {current_user}!"}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Sessão expirada, faça login novamente")

# Rota para registro de usuário
@app.post("/register/")
async def register(user: schemas.UserCreate, db: Session = Depends(db.get_db), authjwt: AuthJWT = Depends()):
    # Verificar se o e-mail já está registrado
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado")

    # Criptografar a senha antes de salvar
    hashed_password = services.get_password_hash(user.password)
    user_obj = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    # Gerar o token JWT
    access_token = authjwt.create_access_token(subject=user_obj.email)

    # Configura o token como um cookie HttpOnly
    response = JSONResponse({"message": "Usuário criado com sucesso"})
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="Strict", max_age=timedelta(minutes=30))
    
    return response

# Função para login
@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(db.get_db), Authorize: AuthJWT = Depends()):
    db_user = services.get_user_by_username(db, username=user.username)
    
    if not db_user or not services.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Gera o token JWT com informações do usuário
    access_token = Authorize.create_access_token(subject=db_user.username, expires_time=timedelta(minutes=30))

    # Configura o token como um cookie HttpOnly apenas em produção
    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=IS_PRODUCTION, 
        samesite="Lax", 
        max_age=1800, # Time for expiration in seconds
        secure=IS_PRODUCTION, 
        domain="localhost" if not IS_PRODUCTION else None
    )

    return response

# Rota para logout (limpa o cookie)
@app.post("/logout/")
def logout(response: JSONResponse):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}
