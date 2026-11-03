from fastapi import APIRouter

router_order = APIRouter(prefix="/orders", tags=["orders"])

@router_order.get("/")
async def hello_orders():
    return {"message": "Hello, Welcome to your deliveri Orders!"}

@router_order.get("/list/")
async def list_orders():
    pedidos = [
        {"id": 1, "item": "Pizza", "quantity": 2},
        {"id": 2, "item": "Burger", "quantity": 1},
        {"id": 3, "item": "Sushi", "quantity": 3}
    ]
    return {"orders": pedidos}