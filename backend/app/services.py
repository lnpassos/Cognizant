from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funções de autenticação
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Funções para manipulação de arquivos
def create_file(db: Session, file_data: schemas.FileCreate, file_path: str, user_id: int):
    db_file = models.File(
        filename=file_data.filename,
        file_path=file_path,
        user_id=user_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_files_by_user(db: Session, user_id: int):
    return db.query(models.File).filter(models.File.user_id == user_id).all()

def get_file_by_id(db: Session, file_id: int):
    return db.query(models.File).filter(models.File.id == file_id).first()

def delete_file(db: Session, file_id: int):
    file = db.query(models.File).filter(models.File.id == file_id).first()
    if file:
        db.delete(file)
        db.commit()
    return file
