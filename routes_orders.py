from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session 
from sqlalchemy.orm import Session
from models import Pedido, Usuario
from schemas import PedidoSchema
from dependencies import verificar_token


router_order = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])


@router_order.get("/")
async def hello_orders():
    return {"message": "Hello, Welcome to your deliveri Orders!"}

@router_order.post("/criar_pedido/")
async def criar_pedido(pedido: PedidoSchema, session: Session = Depends(get_session)):
    novo_pedido = Pedido(usuario_id=pedido.usuario_id, status=pedido.status, preco=pedido.preco)
    session.add(novo_pedido)
    session.commit()
    return {"message": "Pedido criado com sucesso!"} 

@router_order.patch("/criar_pedido/cancelar_pedido/{pedido_id}")
async def cancelar_pedido(pedido_id: int, session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.usuario_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Voce não tem permissão para cancelar este pedido")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400, detail="Pedido já está cancelado")
    pedido.status = "CANCELADO"  # Atualiza o status do pedido para "Cancelado"
    session.commit()
    return {"message": f"Pedido {pedido_id} cancelado com sucesso!",
            "status": pedido.status}
