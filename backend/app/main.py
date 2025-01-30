from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
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
ACCESS_TOKEN_EXPIRE_MINUTES = 1  # Tempo de expiração do token

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
            raise HTTPException(status_code=400, detail="Token inválido")
        return username  # Retorna o nome de usuário que foi salvo no token
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

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
        max_age=30  # 30 minutos
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
        max_age=30  # 30 minutos
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
@app.post("/upload/{folder_name:path}")
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

        # Verifica se a pasta existe no banco de dados pelo caminho completo
        folder = db.query(models.Folder).filter(models.Folder.path == folder_name).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        # Criar a pasta no sistema de arquivos se não existir
        folder_path_full = os.path.join(UPLOAD_FOLDER, db_user.username, folder.path)
        os.makedirs(folder_path_full, exist_ok=True)

        # Salvar arquivo no sistema de arquivos
        file_path = os.path.join(folder_path_full, file.filename)
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
@app.get("/download/{folder_path:path}/{filename}")
def download_file(folder_path: str, filename: str, request: Request, db: Session = Depends(db.get_db)):
    try:
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Busca a pasta exata no banco de dados
        folder = db.query(models.Folder).filter(models.Folder.path == folder_path, models.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada ou não autorizada.")

        # Caminho completo do arquivo no sistema
        folder_full_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_path)
        file_path = os.path.join(folder_full_path, filename)

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

        return FileResponse(file_path, filename=filename)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# Criando uma pasta
@app.post("/create_folder/")
def create_folder(
    folder_path: str = Form(...),  # O nome da pasta será recebido via Form
    db: Session = Depends(db.get_db), 
    file: UploadFile = File(None),  # O arquivo é opcional
    request: Request = None
):
    try:
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder_path = folder_path.strip("/")  # Normalizar o caminho
        existing_folder = db.query(models.Folder).filter(models.Folder.path == folder_path, models.Folder.user_id == db_user.id).first()

        if existing_folder:
            raise HTTPException(status_code=400, detail="Pasta já existe.")

        # Criar a pasta no banco de dados
        folder = models.Folder(path=folder_path, user_id=db_user.id)
        db.add(folder)
        db.commit()
        db.refresh(folder)

        # Criar a estrutura de pastas no sistema de arquivos
        full_folder_path = os.path.join(UPLOAD_FOLDER, db_user.username, folder_path)
        os.makedirs(full_folder_path, exist_ok=True)

        # Upload opcional do arquivo inicial
        if file:
            file_path = os.path.join(full_folder_path, file.filename)
            with open(file_path, "wb") as f:
                f.write(file.file.read())

            # Registrar o arquivo no banco
            new_file = models.File(filename=file.filename, file_path=file_path, folder_id=folder.id)
            db.add(new_file)
            db.commit()

        return {"message": f"Pasta '{folder_path}' criada com sucesso!"}

    except Exception as e:
        print(f"Erro: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

# Listar pastas do usuário
@app.get("/folders/")
def get_folders(db: Session = Depends(db.get_db), request: Request = None):
    try:
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Buscar pastas do usuário no banco de dados
        folders = db.query(models.Folder).filter(models.Folder.user_id == db_user.id).all()

        # Retornar as pastas com o caminho completo
        return [
            {
                "id": folder.id,
                "path": folder.path,  # Caminho completo da pasta
                "name": folder.path.split("/")[-1],  # Nome da última pasta no caminho
                "user_id": folder.user_id
            }
            for folder in folders
        ]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    
    
# Rota para listar arquivos de uma pasta
@app.get("/folders/{folder_path:path}/files/")
def get_files_in_folder(folder_path: str, db: Session = Depends(db.get_db), request: Request = None):
    try:
        current_user = get_current_user(request)
        db_user = db.query(models.User).filter(models.User.username == current_user).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        folder = db.query(models.Folder).filter(models.Folder.path == folder_path, models.Folder.user_id == db_user.id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Pasta não encontrada.")

        files = db.query(models.File).filter(models.File.folder_id == folder.id).all()

        return [{"id": file.id, "filename": file.filename, "file_path": file.file_path, "uploaded_at": file.uploaded_at} for file in files]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
