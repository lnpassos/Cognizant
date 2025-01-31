from sqlalchemy.orm import Session
from .. import models, schemas

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
