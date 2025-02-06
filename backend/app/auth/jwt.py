from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Request
from pydantic import BaseModel

# Configurações
SECRET_KEY = "kj45k4jhg51g5jfh4f85gh1g5j1hj5fgh4gd4h"  # Coloque uma chave segura aqui
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Modelo de dados para o token
class TokenData(BaseModel):
    email: str


# Classe para gerenciar autenticação
class AuthHandler:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt


    def decode_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Token inválido")
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expirado")
            return TokenData(email=email)
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")


    def get_current_user(self, request: Request) -> str:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Token não encontrado")
        token_data = self.decode_token(token)
        return token_data.email
