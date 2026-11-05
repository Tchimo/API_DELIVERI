from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException
from models import banco, Usuario, Item  # banco = engine (ajuste se for outro nome)
from jose import jwt, JWTError
from auth_config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login_form/")
SessionLocal = sessionmaker(bind=banco)

def get_session():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(payload.get("sub"))
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Acesso inválido: Usuário não encontrado")
        return usuario
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
def calcular_preco_total(pedido_id: int, session: Session):
    itens = session.query(Item).filter(Item.pedido_id == pedido_id).all()
    preco_total = sum(item.preco_unitario * item.quantidade for item in itens)
    return preco_total

def listar_itens_pedido(pedido_id: int, session: Session):
    itens = session.query(Item).filter(Item.pedido_id == pedido_id).all()
    return [
        {
            "id": i.id,
            "quantidade": i.quantidade,
            "preco_unitario": i.preco_unitario,
            "subtotal": i.quantidade * i.preco_unitario,
        }
        for i in itens
    ]