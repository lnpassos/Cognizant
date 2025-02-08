from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Request
from pydantic import BaseModel


load_dotenv()

""" 
    For better security, in a real production system, we can configure the API key using Docker, 
    Kubernetes Secrets, or directly as an environment variable on the server. 
"""

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Data model for token
class TokenData(BaseModel):
    email: str


# Authentication handler class
class AuthHandler:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        # Generate a JWT access token with expiration.
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenData:
        # Decode and validate the JWT token.
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")
            return TokenData(email=email)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    def get_current_user(self, request: Request) -> str:
        # Retrieve the current user from the request cookies.
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Token not found")
        token_data = self.decode_token(token)
        return token_data.email
