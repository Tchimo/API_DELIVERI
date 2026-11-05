from sqlalchemy import String, create_engine, Column, Integer, ForeignKey, Boolean, Float
from sqlalchemy.orm import declarative_base


banco = create_engine('sqlite:///banco_de_dados.db')  # conexão do banco de dados

Base = declarative_base()  # base para as classes/tabelas do modelo

# criação das tabelas no banco de dados
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(50), nullable=False)
    email = Column("email", String(100), nullable=False, unique=True)
    senha = Column("senha", String(100), nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String, nullable=False)
    preco = Column("preco", Float, nullable=False)
    usuario_id = Column("usuario_id", Integer, ForeignKey('usuarios.id'), nullable=False)

    def __init__(self, usuario_id, status="PENDENTE", preco=0.0):
        self.usuario_id = usuario_id
        self.status = status
        self.preco = preco

class Item(Base):
    __tablename__ = 'itens'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer, nullable=False)
    preco_unitario = Column("preco_unitario", Float, nullable=False)
    pedido_id = Column("pedido_id", Integer, ForeignKey('pedidos.id'), nullable=False)

    def __init__(self, preco_unitario, quantidade, pedido_id):
        self.preco_unitario = preco_unitario
        self.quantidade = quantidade
        self.pedido_id = pedido_id


        #alembic revision --autogenerate -m "Inicial migration" 
        #alembic upgrade head