from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import users, folders, chatbot
from app.db import Base, engine

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost",
]
# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(users.router)
app.include_router(folders.router)
app.include_router(chatbot.router)


@app.get("/")
def read_root():
    return {"message": "API Running.."}
