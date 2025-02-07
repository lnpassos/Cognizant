from sqlalchemy.orm import Session
from app.models import users as models
from app.schemas import users as schemas
from app.auth.jwt import AuthHandler
from app.utils.utils import (
    validate_email_format,
    get_password_hash,
    verify_password as utils_verify_password,
)
from fastapi import HTTPException

auth_handler = AuthHandler()


# Function to generate the access token
def generate_access_token(user_obj):
    return auth_handler.create_access_token(data={"sub": user_obj.email})


# Function to retrieve a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Function to verify the password (fixed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return utils_verify_password(plain_password, hashed_password)


# Function to register a new user
def register_user(user: schemas.UserCreate, db: Session):
    if not validate_email_format(user.email):
        raise HTTPException(status_code=400, detail="Invalid email")

    # Check if the email is already registered
    existing_user_by_email = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Encrypt the password
    hashed_password = get_password_hash(user.password)

    user_obj = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj
