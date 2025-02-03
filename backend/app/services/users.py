import re
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import users as models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funções de autenticação
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
def validate_email_format(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None
