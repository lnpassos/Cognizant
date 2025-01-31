from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
from fastapi import Request

SECRET_KEY = "kj45k4jhg51g5jfh4f85gh1g5j1hj5fgh4gd4h" # Include a secure key here (using .pem file for example)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    token = request.cookies.get("access_token") 
    if not token:
        raise HTTPException(status_code=401, detail="Token não encontrado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Token inválido")
        return username  # Retorna o nome de usuário que foi salvo no token
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
