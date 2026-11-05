#get-> leitura/pegar
#post-> criação
#put/patch-> atualização
#delete-> remoção

from fastapi import FastAPI
from routes_auth import router_auth 
from routes_orders import router_order


app = FastAPI()

app.include_router(router_auth)
app.include_router(router_order)

#uvicorn main:app --reload