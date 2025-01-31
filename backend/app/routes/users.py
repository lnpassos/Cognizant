from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import users as models
from app.schemas import users as schemas
from app.services import users as services
from app.auth.jwt import create_access_token

router = APIRouter()
print("Rota de usuários carregada!")

# Registro de usuário
@router.post("/register/")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já registrado")

    hashed_password = services.get_password_hash(user.password)
    user_obj = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    access_token = create_access_token(data={"sub": user_obj.email})

    response = JSONResponse({"message": "Usuário criado com sucesso"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="Lax",
        secure=True,
        max_age=30 * 60  
    )
    
    return response

# Função para login
@router.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = services.get_user_by_username(db, username=user.username)
    
    if not db_user or not services.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    access_token = create_access_token(data={"sub": db_user.username})

    response = JSONResponse({"message": "Login realizado com sucesso"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True, 
        samesite="Lax", 
        secure=True,
        max_age=30 * 60 
    )

    return response


# Função para logout (limpa o cookie)
@router.post("/logout/")
def logout():
    response = JSONResponse({"message": "Logout realizado com sucesso"})
    response.delete_cookie("access_token")
    return response
