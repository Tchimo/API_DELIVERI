from pydantic import BaseModel, EmailStr
from typing import Optional

class CadastroSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    ativo: Optional[bool] = True
    admin: Optional[bool] = False

    class Config:
        from_attributes = True  # Permite a criação de instâncias a partir de objetos ORM


class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True  # Permite a criação de instâncias a partir de objetos ORM


class PedidoSchema(BaseModel):
    usuario_id: int
    status: str = "Pendente"
    preco: float = 0.0

    class Config:
        from_attributes = True  # Permite a criação de instâncias a partir de objetos ORM


class ItemSchema(BaseModel):
    preco_unitario: float
    quantidade: int
    
    class Config:
        from_attributes = True  # Permite a criação de instâncias a partir de objetos ORM