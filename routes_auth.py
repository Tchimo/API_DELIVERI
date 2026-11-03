from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session, sessionmaker
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from models import Usuario, banco  # banco = engine (ajuste se for outro nome)

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
SECRET_KEY = os.getenv("SECRET_KEY")  # Obtém a chave
SessionLocal = sessionmaker(bind=banco)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router_auth = APIRouter(prefix="/auth", tags=["auth"])


class CadastroSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str


def get_session():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()


@router_auth.get("/")
async def hello_auth():
    return {"message": "Hello, Welcome to your deliveri Auth!"}


@router_auth.post("/cadastro/", status_code=201)
def register(dados: CadastroSchema, session: Session = Depends(get_session)):
    usuario_existente = session.query(Usuario).filter(Usuario.email == dados.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = Usuario(nome=dados.nome, email=dados.email, senha=bcrypt_context.hash(dados.senha))
    session.add(novo_usuario)
    session.commit()
    return {"message": "Cadastro realizado com sucesso"}

"""@router_auth.post("/login/")
def login(dados: CadastroSchema, session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not bcrypt_context.verify(dados.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"message": "Login realizado com sucesso"}
"""