from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, services, db
from jose import JWTError, jwt
from fastapi.responses import JSONResponse, FileResponse
from fastapi import Request
import os

# Configurações JWT
SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tempo de expiração do token

# Função para gerar o token de acesso
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Função para verificar o token JWT
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token não encontrado")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username  # Retorna o nome de usuário que foi salvo no token
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

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

# Função para registro de usuário
@app.post("/register/")
async def register(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
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
        max_age=1800  # 30 minutos
    )
    
    return response

# Função para login
@app.post("/login/")
def login(user: schemas.UserLogin, db: Session = Depends(db.get_db)):
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
        max_age=1800  # 30 minutos
    )

    return response

# Função para home (acesso protegido)
@app.get("/home/")
def home(request: Request):
    try:
        current_user = get_current_user(request)
        return {"message": f"Bem-vindo, {current_user}!"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Sessão expirada, faça login novamente")

# Função para logout (limpa o cookie)
@app.post("/logout/")
def logout(response: JSONResponse):
    response.delete_cookie("access_token")
    return {"message": "Logout realizado com sucesso"}

# Pasta para armazenar uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Rota para upload de arquivo
@app.post("/upload/{folder_name}")
async def upload_file(
    folder_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(db.get_db),
    request: Request = None
):
    try:
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Verifica se a pasta existe no banco de dados
        folder = db.query(models.Folder).filter(models.Folder.name == folder_name, models.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        # Criar a pasta no sistema de arquivos se não existir
        folder_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Salvar arquivo no sistema de arquivos
        file_path = os.path.join(folder_path, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Salvar informações do arquivo no banco de dados
        new_file = models.File(
            filename=file.filename,
            file_path=file_path,
            user_id=db_user.id,
            folder_id=folder.id
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        return {"message": "Arquivo enviado com sucesso", "file": new_file.filename}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rota para download de arquivo
@app.get("/download/{folder_name}/{filename}")
def download_file(folder_name: str, filename: str, request: Request = None, db: Session = Depends(db.get_db)):
    try:
        # Obtém o usuário autenticado
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Verifica se a pasta pertence ao usuário
        folder = db.query(models.Folder).filter(models.Folder.name == folder_name, models.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada ou não autorizada.")

        # Caminho completo do arquivo no sistema de arquivos, incluindo o nome do usuário
        folder_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_name)
        file_path = os.path.join(folder_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        # Retorna o arquivo para o usuário
        response = FileResponse(file_path, filename=filename)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Criando uma pasta
@app.post("/create_folder/")
def create_folder(request: Request, request_data: schemas.FolderCreate, db: Session = Depends(db.get_db)):
    try:
        get_current_user(request)
        
        # Recupera o nome de usuário a partir do token
        current_user = get_current_user(request)

        db_user = db.query(models.User).filter(models.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder_name = request_data.folder_name  # Usando request_data para o nome da pasta
        folder = models.Folder(name=folder_name, user_id=db_user.id)

        db.add(folder)
        db.commit()
        db.refresh(folder)

        folder_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        return {"message": f"Pasta '{folder_name}' criada com sucesso!"}

    except Exception as e:
        print(f"Erro: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido ou não fornecido.")

# Listar pastas do usuário
@app.get("/folders/")
def get_folders(db: Session = Depends(db.get_db), request: Request = None):
    try:
        get_current_user(request)

        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folders = db.query(models.Folder).filter(models.Folder.user_id == db_user.id).all()

        return [{"name": folder.name} for folder in folders]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rota para listar arquivos de uma pasta
@app.get("/folders/{folder_name}/files/")
def get_files_in_folder(folder_name: str, db: Session = Depends(db.get_db), request: Request = None):
    try:
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Buscar a pasta no banco de dados
        folder = db.query(models.Folder).filter(models.Folder.name == folder_name, models.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        # Buscar arquivos no banco de dados
        files = db.query(models.File).filter(models.File.folder_id == folder.id).all()

        return [{"id": file.id, "filename": file.filename, "file_path": file.file_path, "uploaded_at": file.uploaded_at} for file in files]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
