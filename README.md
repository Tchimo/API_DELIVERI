# Deliveri API

API REST para gerenciamento de usuários, pedidos e itens de pedidos, construída com FastAPI, SQLAlchemy e SQLite.

**Status do projeto:** Concluído.

## Recursos

- Cadastro e autenticação de usuários.
- Autenticação por token JWT.
- Criação, consulta, finalização e cancelamento de pedidos.
- Inclusão e remoção de itens, com recálculo do valor total.
- Controle de acesso para operações de clientes e administradores.
- Migrações de banco de dados com Alembic.
- Documentação interativa fornecida pelo FastAPI.

## Tecnologias

- Python
- FastAPI e Uvicorn
- SQLAlchemy
- SQLite
- Alembic
- JWT (`python-jose`) e hash de senhas (`passlib`)

## Pré-requisitos

- Python instalado.
- Git, caso queira clonar o repositório.

## Instalação e execução

No PowerShell, na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requeriments.txt
```

Configure as variáveis de ambiente em um arquivo `.env` na raiz do projeto:

```dotenv
SECRET_KEY=coloque-uma-chave-secreta-forte-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Gere uma chave secreta localmente, sem compartilhar ou versionar o valor:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Crie ou atualize as tabelas do banco:

```powershell
alembic upgrade head
```

Inicie o servidor de desenvolvimento:

```powershell
uvicorn main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`. A documentação interativa pode ser acessada em:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

O SQLite usa o arquivo `banco_de_dados.db` na pasta do projeto.

## Autenticação

As rotas de pedidos exigem um token JWT. Faça login e envie o token retornado no cabeçalho:

```http
Authorization: Bearer <access_token>
```

O endpoint `/auth/login/` recebe JSON. O endpoint `/auth/login_form/` recebe os campos `username` (o e-mail cadastrado) e `password` como formulário OAuth2.

## Endpoints

### Autenticação — `/auth`

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/auth/` | Público | Mensagem de boas-vindas |
| `POST` | `/auth/cadastro/` | Público | Cadastra um usuário |
| `POST` | `/auth/login/` | Público | Autentica com JSON e retorna tokens de acesso e atualização |
| `POST` | `/auth/login_form/` | Público | Autentica usando formulário OAuth2 e retorna token de acesso |
| `POST` | `/auth/refresh/` | Token válido | Emite um novo token de acesso |

Exemplo de cadastro:

```json
{
  "nome": "Maria",
  "email": "maria@example.com",
  "senha": "uma-senha-forte",
  "ativo":true,
  "Admin":false(por padrão, pode alterar pra true se o usuário e admin)
}
```

Os campos `ativo` e `admin` têm valores padrão (`true` e `false`, respectivamente). **Atenção:** no código atual, o endpoint público de cadastro também aceita esses campos enviados no corpo da requisição. Não exponha essa implementação em produção sem restringir a atribuição de privilégios administrativos a um processo confiável no servidor.

Exemplo de login:

```json
{
  "email": "maria@example.com",
  "senha": "uma-senha-forte"
}
```

### Pedidos — `/pedidos`

Todas as rotas abaixo exigem autenticação.

| Método | Rota | Acesso adicional | Descrição |
|---|---|---|---|
| `GET` | `/pedidos/` | Usuário autenticado | Mensagem de boas-vindas |
| `POST` | `/pedidos/criar_pedido/` | Usuário autenticado | Cria um pedido para o usuário autenticado |
| `GET` | `/pedidos/meus_pedidos/` | Usuário autenticado | Lista os pedidos do usuário autenticado |
| `PATCH` | `/pedidos/cancelar_pedido/{pedido_id}` | Dono do pedido ou administrador | Cancela um pedido |
| `PATCH` | `/pedidos/finalizar_pedido/{pedido_id}` | Dono do pedido ou administrador | Finaliza um pedido |
| `POST` | `/pedidos/adicionar_item/{pedido_id}` | Dono do pedido ou administrador | Adiciona item e atualiza o total |
| `DELETE` | `/pedidos/remover_item/{item_id}` | Dono do pedido ou administrador | Remove item e atualiza o total |
| `GET` | `/pedidos/listar_pedidos/` | Administrador | Lista todos os pedidos |
| `GET` | `/pedidos/pedido/{pedido_id}` | Administrador | Consulta um pedido específico |

Exemplo de corpo para adicionar um item:

```json
{
  "preco_unitario": 25.9,
  "quantidade": 2
}
```

O pedido é criado com status `PENDENTE` e total inicial `0.0`. Os itens alteram o total do pedido. Um pedido pode ser finalizado ou cancelado conforme seu estado atual; pedidos cancelados não aceitam novos itens nem podem ser finalizados.

## Banco de dados e migrações

O banco SQLite é configurado em `models.py`. As migrações ficam em `alembic/versions/`.

Para aplicar as migrações:

```powershell
alembic upgrade head
```

Para criar uma nova migração após alterar os modelos:

```powershell
alembic revision --autogenerate -m "descricao da alteracao"
alembic upgrade head
```

Revise as migrações geradas antes de aplicá-las, especialmente em ambientes com dados existentes.

## Segurança

- Mantenha `.env`, chaves JWT e bancos de dados locais fora do controle de versão.
- Use uma `SECRET_KEY` forte e exclusiva em cada ambiente.
- Senhas são armazenadas com hash; nunca envie senhas ou tokens em logs.
- Restrinja a criação de administradores a um fluxo confiável no servidor antes de disponibilizar o cadastro publicamente.
- Configure HTTPS e variáveis de ambiente apropriadas antes de implantar a API em produção.

## Estrutura do projeto

```text
.
├── alembic/             # Configuração e versões das migrações
├── auth_config.py       # Configurações de JWT carregadas do ambiente
├── dependencies.py      # Sessão do banco e dependências compartilhadas
├── main.py              # Aplicação FastAPI e registro das rotas
├── models.py            # Modelos SQLAlchemy e conexão SQLite
├── routes_auth.py       # Rotas de cadastro e autenticação
├── routes_orders.py     # Rotas de pedidos e itens
├── schemas.py           # Schemas de validação da API
└── requeriments.txt     # Dependências Python do projeto
```

## Licença

Nenhuma licença foi especificada neste repositório.
