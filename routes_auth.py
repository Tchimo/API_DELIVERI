from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from models import Usuario 
from dependencies import get_session, verificar_token
from schemas import CadastroSchema, LoginSchema
from jose import jwt
from datetime import datetime, timedelta, timezone
from auth_config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY



bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router_auth = APIRouter(prefix="/auth", tags=["auth"])
 

def criar_token(usuario_id: int, duracao: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao
    dicionario_inf = {"sub": str(usuario_id), "exp": data_expiracao}
    token = jwt.encode(dicionario_inf, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router_auth.get("/")
async def hello_auth():
    return {"message": "Hello, Welcome to your deliveri Auth!"}


@router_auth.post("/cadastro/", status_code=201)
async def register(dados: CadastroSchema, session: Session = Depends(get_session)):
    usuario_existente = session.query(Usuario).filter(Usuario.email == dados.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = Usuario(nome=dados.nome,
                           email=dados.email,
                           senha=bcrypt_context.hash(dados.senha),
                           ativo=dados.ativo,
                           admin=dados.admin,
                           )
    session.add(novo_usuario)
    session.commit()
    return {"message": "Cadastro realizado com sucesso"}


@router_auth.post("/login/")
async def login(dados: LoginSchema, session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not bcrypt_context.verify(dados.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas") 
    else:
        acess_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao=timedelta(days=7))  # Cria um token de atualização (refresh token) 
        return {"message": "Login realizado com sucesso", 
                "access_token": acess_token, 
                "refresh_token": refresh_token,
                "token_type": "bearer"}

@router_auth.post("/login_form/")
async def login_form(dados: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.email == dados.username).first()
    if not usuario or not bcrypt_context.verify(dados.password, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    else:
        acess_token = criar_token(usuario.id)
        return {"message": "Login realizado com sucesso", 
                "access_token": acess_token, 
                "token_type": "bearer"}

@router_auth.post("/refresh/")
async def refresh_token(usuario: Usuario = Depends(verificar_token)):
    novo_access_token = criar_token(usuario.id)
    return {"access_token": novo_access_token, "token_type": "bearer"}
