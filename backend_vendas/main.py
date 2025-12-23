import os
from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import SessionLocal
from models import Cliente
from datetime import date, datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt

# -------------------------------
# CONFIGURAÇÕES DE SEGURANÇA
# -------------------------------
SECRET_KEY = "LEDAX_GEO_VENDAS_SECRET_KEY_MUDE_ISSO_EM_PRODUCAO"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120 # Token dura 2 horas

# Contexto de criptografia (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="API DE VENDAS LEDAX")

# -------------------------------
# 1. Configurações (CORS)
# -------------------------------
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 2. BANCO DE DADOS E DEPENDÊNCIAS
# -------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# 3. SISTEMA DE USUÁRIOS (FAKE DB)
# -------------------------------
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$XwELC5ii7NP2ZZ2fAnR2CuCtEuywnNRsYU0wT5FGXWhz/iITB1gh6",
        "permissoes": ["vendas", "redes", "uc"] 
    },
    "gestor_redes": {
        "username": "gestor_redes",
        "hashed_password": "$2b$12$XwELC5ii7NP2ZZ2fAnR2CuCtEuywnNRsYU0wT5FGXWhz/iITB1gh6",
        "permissoes": ["redes"] 
    },
    "analista_uc": {
        "username": "analista_uc",
        "hashed_password": "$2b$12$XwELC5ii7NP2ZZ2fAnR2CuCtEuywnNRsYU0wT5FGXWhz/iITB1gh6",
        "permissoes": ["uc"] 
    }
}

# Funções Auxiliares de Auth
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# -------------------------------
# 4. ROTA DE LOGIN (GERAR TOKEN)
# -------------------------------
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "permissoes": user.get('permissoes', []),
        "username": user['username']
    }

# -------------------------------
# 5. Lógica de Filtros (ATUALIZADA)
# -------------------------------
def apply_filters_to_query(query, rede, tipo_cliente, funil, representante, regiao, responsavel, uf, data_inicio, data_fim, valor_min, valor_max, busca_texto):
    
    # Filtros de Lista (List[str])
    if rede: query = query.filter(Cliente.rede.in_(rede)) 
    if tipo_cliente: query = query.filter(Cliente.tipo_cliente.in_(tipo_cliente))
    if funil: query = query.filter(Cliente.funil.in_(funil))
    if representante: query = query.filter(Cliente.representante.in_(representante))
    if regiao: query = query.filter(Cliente.regiao.in_(regiao))
    if responsavel: query = query.filter(Cliente.responsavel.in_(responsavel))
    if uf: query = query.filter(Cliente.uf.in_(uf))

    # Filtros de Data e Valor
    if data_inicio: query = query.filter(Cliente.data >= data_inicio)
    if data_fim: query = query.filter(Cliente.data <= data_fim)
    
    # Filtros de Faixa de Valor
    if valor_min is not None: query = query.filter(Cliente.valor_venda >= valor_min)
    if valor_max is not None: query = query.filter(Cliente.valor_venda <= valor_max)

    # Filtro de Busca Textual
    if busca_texto:
        termo = f"%{busca_texto.upper()}%"
        query = query.filter(
            or_(
                Cliente.titulo.ilike(termo),
                Cliente.endereco_cliente.ilike(termo),
                Cliente.local_de_entrega.ilike(termo),
                Cliente.cidade.ilike(termo),
                Cliente.uf.ilike(termo),
                Cliente.rede.ilike(termo),
            )
        )

    # Garante que tem coordenadas
    query = query.filter(Cliente.latitude != None, Cliente.longitude != None)
    return query

# -------------------------------
# 6. ENDPOINTS API PROTEGIDOS
# -------------------------------

@app.get("/")
def root():
    return {"status": "API Vendas Segura rodando na porta 8001"}

# --- NOVA ROTA: DATA DE ATUALIZAÇÃO DO ARQUIVO DB ---
@app.get("/api/vendas/status-dados")
def get_status_dados(current_user: dict = Depends(get_current_user)):
    """
    Retorna a data e hora da última modificação do arquivo vendas.db.
    Isso serve para informar ao usuário quão recentes são os dados.
    """
    try:
        # Nomes prováveis do banco de dados (ajuste se seu arquivo tiver outro nome)
        caminhos_possiveis = ["ledax.db", "data/ledax.db", "backend/ledax.db"]
        caminho_db = None

        for caminho in caminhos_possiveis:
            if os.path.exists(caminho):
                caminho_db = caminho
                break
        
        if not caminho_db:
            return {"data_atualizacao": "Banco não localizado"}
            
        # Pega o timestamp da última modificação do arquivo
        timestamp = os.path.getmtime(caminho_db)
        
        # Converte para um formato legível
        # Ajuste o fuso horário se necessário (aqui pega o horário do servidor/máquina)
        data_formatada = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y às %H:%M")
        
        return {"data_atualizacao": data_formatada}
    except Exception as e:
        return {"data_atualizacao": "Indisponível"}


@app.get("/api/vendas/filtros")
def get_filtros(
    rede: Optional[List[str]] = Query(None),
    tipo_cliente: Optional[List[str]] = Query(None),
    funil: Optional[List[str]] = Query(None),
    representante: Optional[List[str]] = Query(None),
    regiao: Optional[List[str]] = Query(None),
    responsavel: Optional[List[str]] = Query(None),
    uf: Optional[List[str]] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    busca_texto: Optional[str] = Query(None),    
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    base_query = db.query(Cliente)
    
    # Aplica os filtros atuais para gerar o "faceting" (opções restantes)
    base_query = apply_filters_to_query(
        base_query, rede, tipo_cliente, funil, representante, regiao, responsavel, uf, 
        data_inicio, data_fim, valor_min, valor_max, busca_texto
    )

    def uniq_filtered(col):
        # helper para extrair valores únicos
        vals = base_query.with_entities(getattr(Cliente, col)).distinct().all()
        return sorted([v[0] for v in vals if v[0]])

    return {
        "rede": uniq_filtered("rede"),
        "tipo_cliente": uniq_filtered("tipo_cliente"),
        "funil": uniq_filtered("funil"),
        "representante": uniq_filtered("representante"),
        "regiao": uniq_filtered("regiao"),
        "responsavel": uniq_filtered("responsavel"),
        "uf": uniq_filtered("uf"),
    }

@app.get("/api/vendas/dados")
def get_vendas_dados(
    rede: Optional[List[str]] = Query(None),
    tipo_cliente: Optional[List[str]] = Query(None),
    funil: Optional[List[str]] = Query(None),
    representante: Optional[List[str]] = Query(None),
    regiao: Optional[List[str]] = Query(None),
    responsavel: Optional[List[str]] = Query(None),
    uf: Optional[List[str]] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    busca_texto: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Cliente)
    query = apply_filters_to_query(
        query, rede, tipo_cliente, funil, representante, regiao, responsavel, uf,
        data_inicio, data_fim, valor_min, valor_max, busca_texto
    )
    
    return query.all()