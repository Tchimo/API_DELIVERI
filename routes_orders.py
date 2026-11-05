from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_session, listar_itens_pedido, verificar_token, calcular_preco_total
from sqlalchemy.orm import Session
from models import Pedido, Usuario, Item
from schemas import PedidoSchema, ItemSchema


router_order = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])


@router_order.get("/")
async def hello_orders():
    return {"message": "Hello, Welcome to your deliveri Orders!"}

"""@router_order.post("/criar_pedido/")
async def criar_pedido(pedido: PedidoSchema, session: Session = Depends(get_session)):
    novo_pedido = Pedido(usuario_id=pedido.usuario_id, status=pedido.status, preco=pedido.preco)
    session.add(novo_pedido)
    session.commit()
    return {"message": "Pedido criado com sucesso!"}"""

@router_order.post("/criar_pedido/")
async def criar_pedido(session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    novo_pedido = Pedido(usuario_id=usuario.id)
    session.add(novo_pedido)
    session.commit()
    return {"message": "Pedido criado com sucesso!"}
 

@router_order.patch("/cancelar_pedido/{pedido_id}")
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

@router_order.get("/listar_pedidos/")
async def listar_pedidos(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(verificar_token),
):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem permissão para fazer essa operação")

    pedidos = session.query(Pedido).all()

    resultado = []
    for pedido in pedidos:
        itens = listar_itens_pedido(pedido.id, session)
        resultado.append({
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "status": pedido.status,
            "preco_total": pedido.preco,
            "quantidade_itens": len(itens),
            "itens": itens,
        })

    return {"quantidade_pedidos": len(resultado), "pedidos": resultado}

@router_order.post("/adicionar_item/{pedido_id}")
async def adicionar_item(pedido_id: int, item: ItemSchema, session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.usuario_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Voce não tem permissão para adicionar itens a este pedido")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400, detail="Não é possível adicionar itens a um pedido cancelado")
    
    novo_item = Item(preco_unitario=item.preco_unitario, quantidade=item.quantidade, pedido_id=pedido_id)
    session.add(novo_item)
    # Atualiza o preço total do pedido
    session.flush()  # grava o item para entrar na soma
    pedido.preco = calcular_preco_total(pedido_id, session)
    session.commit()

    itens_restantes = session.query(Item).filter(Item.pedido_id == pedido_id).all()
    
    return {
        "message": f"Item adicionado ao pedido {pedido_id} com sucesso!",
        #"item_id": novo_item.id,
        "pedido": {
            "id": pedido.id,
            "status": pedido.status,
            "usuario_id": pedido.usuario_id,
            "preco_total": pedido.preco,
        },
        "quantidade_itens": len(itens_restantes),
        "itens": itens_restantes,
    }

@router_order.delete("/remover_item/{item_id}")
async def remover_item(
    item_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(verificar_token),
):
    item = session.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    pedido = session.query(Pedido).filter(Pedido.id == item.pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.usuario_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover itens deste pedido")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400, detail="Não é possível remover itens de um pedido cancelado")

    pedido_id = pedido.id
    session.delete(item)
    session.flush()
    pedido.preco = calcular_preco_total(pedido_id, session)
    session.commit()

    itens_restantes = session.query(Item).filter(Item.pedido_id == pedido_id).all()

    return {
        "message": f"Item {item_id} removido do pedido {pedido_id} com sucesso!",
        #"novo_preco_total": pedido.preco,
        "pedido": {
                    "id": pedido.id,
                    "status": pedido.status,
                    "usuario_id": pedido.usuario_id,
                    "preco_total": pedido.preco,
                },  
        "quantidade_itens": len(itens_restantes),
        "itens_restantes": [
            {
                "id": i.id,
                "quantidade": i.quantidade,
                "preco_unitario": i.preco_unitario,
                "subtotal": i.quantidade * i.preco_unitario,
            }
            for i in itens_restantes
        ],
    }

@router_order.patch("/finalizar_pedido/{pedido_id}")
async def finalizar_pedido(pedido_id: int, session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.usuario_id != usuario.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Voce não tem permissão para finalizar este pedido")
    if pedido.status == "CANCELADO":
        raise HTTPException(status_code=400, detail="Não é possível finalizar um pedido cancelado")
    if pedido.status == "FINALIZADO":
        raise HTTPException(status_code=400, detail="Pedido já está finalizado")
    pedido.status = "FINALIZADO"  # Atualiza o status do pedido para "Finalizado"
    session.commit()
    itens = listar_itens_pedido(pedido_id, session)

    return {
        "message": f"Pedido {pedido_id} finalizado com sucesso!",
        "pedido": {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco_total": pedido.preco,
            "status": pedido.status,
        },
        "quantidade_itens": len(itens),
        "itens": itens,
    }

@router_order.get("/pedido/{pedido_id}")
async def obter_pedido(pedido_id: int, session: Session = Depends(get_session), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Voce não tem permissão para acessar este pedido")
    
    itens = listar_itens_pedido(pedido_id, session)

    return {
        "pedido": {
            "id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "preco_total": pedido.preco,
            "status": pedido.status,
        },
        "quantidade_itens": len(itens),
        "itens": itens,
    }

@router_order.get("/meus_pedidos/")
async def meus_pedidos(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(verificar_token),
):
    pedidos = session.query(Pedido).filter(Pedido.usuario_id == usuario.id).all()
    return {
        "pedidos": [
            {
                "id": p.id,
                "status": p.status,
                "preco_total": p.preco,
                "itens": listar_itens_pedido(p.id, session),
            }
            for p in pedidos
        ]
    }