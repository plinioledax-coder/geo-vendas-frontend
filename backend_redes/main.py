from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from models import LojaRede

# Removido: Imports de arquivos estáticos (os, StaticFiles, FileResponse) 
# pois agora o Vue (frontend) roda separado em desenvolvimento.

app = FastAPI(title="LEDAX REDES MAPA API")

# ----------------------------------------------------
# 1. Configuração de Middleware (CRUCIAL PARA O VUE)
# ----------------------------------------------------

origins = [
    "http://localhost:5173",    # Porta padrão do Vite/Vue
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*" # Permite tudo (bom para dev, cuidado em produção)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Autoriza o Vue a pedir dados
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 2. Dependency Injection
# ----------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------
# 3. Rotas da API
# ----------------------------------------------------

@app.get("/api/lojas_rede/")
def get_lojas_rede(db: Session = Depends(get_db)):
    """
    Endpoint consumido pelo RedesView.vue
    Retorna JSON com as lojas e status de venda.
    """
    # Filtra apenas os registros que possuem coordenadas
    lojas = db.query(LojaRede).filter(
        LojaRede.latitude != None, 
        LojaRede.longitude != None
    ).all()

    # Retorna lista de dicionários (JSON array)
    return [{
        "id": loja.id,
        "rede": loja.rede,
        "loja": loja.loja,
        "endereco": loja.endereco,
        "cnpj": loja.cnpj,
        "data_venda": loja.data_ultima_venda.isoformat() if loja.data_ultima_venda else None,
        "latitude": loja.latitude,
        "longitude": loja.longitude,
        "teve_venda": loja.teve_venda, 
        "funil_ultima_venda": loja.funil_ultima_venda 
    } for loja in lojas]

# ----------------------------------------------------
# 4. Rota de Teste (Opcional)
# ----------------------------------------------------
@app.get("/")
def root():
    return {"message": "API Rodando"}

# ADICIONE ISSO NO FINAL SE VOCE RODA O ARQUIVO DIRETO PELO PYTHON
if __name__ == "__main__":
    import uvicorn
    # Aqui também adicionamos o reload_dirs para evitar olhar a venv
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_excludes=["venv"])