import logging
import os

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from sqlalchemy import text

from db import Base, engine, get_db
from auth import router as auth_router
from notes import router as notes_router
from audit_routes import router as audit_router
from admin_routes import router as admin_router
# IMPORTANTE: nenhuma rota de AI aqui.
# from ai_routes import router as ai_router


# ---------------------------
# LOGGING BÁSICO
# ---------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger("fastapi-platform-lab")


# ---------------------------
# APP FASTAPI (TEMA DARK / NEON)
# ---------------------------

app = FastAPI(
    title="FastAPI Platform Lab API",
    version="1.0.0",
    description=(
        "Backend oficial do FastAPI Platform Lab: autenticação, notas, auditoria e módulo administrativo."
    ),
    swagger_ui_parameters={
        # tema de highlight escuro (preto/neon)
        "syntaxHighlight": {"theme": "obsidian"},
        # começa tudo recolhido
        "docExpansion": "none",
        # mostra tempo de resposta em cada request
        "displayRequestDuration": True,
        # esconde a árvore gigante de modelos por padrão
        "defaultModelsExpandDepth": -1,
    },
)


# ---------------------------
# CORS
# Lê origens permitidas de ALLOWED_ORIGINS (CSV).
# Exemplo: ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
# Default: apenas localhost para desenvolvimento local.
# ---------------------------

_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# MIDDLEWARE DE LOG DE REQUISIÇÕES
# ---------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Loga toda requisição:
    - método + rota na entrada
    - método + rota + status na saída
    """
    logger.info(f"REQUEST {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(
        f"RESPONSE {request.method} {request.url.path} -> {response.status_code}"
    )
    return response


# ---------------------------
# STARTUP (DEV): CRIA TABELAS
# ---------------------------

@app.on_event("startup")
def on_startup() -> None:
    """
    Em dev:
    - garante que as tabelas existam.
    Em produção: usar migrações (Alembic).
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Banco inicializado (create_all executado).")


# ---------------------------
# REGISTRO DE ROTAS PRINCIPAIS
# ---------------------------

# Autenticação: /signup, /login, /me
app.include_router(auth_router)

# Notas autenticadas: /notes
app.include_router(notes_router)

# Auditoria (admin): /audit/logs
app.include_router(audit_router)

# Admin: /admin/users, /admin/promote/{user_id}, etc.
app.include_router(admin_router)

# Nenhuma rota de AI registrada.
# app.include_router(ai_router)


# ---------------------------
# LIMPEZA FORÇADA DE ROTAS /ai*
# ---------------------------

def remove_ai_routes() -> None:
    """
    Remove qualquer rota que comece com /ai do app,
    mesmo que tenha sido registrada em outro lugar.
    Só por garantia.
    """
    original_routes = list(app.router.routes)
    new_routes = []
    removed = []

    for route in original_routes:
        if isinstance(route, APIRoute) and route.path.startswith("/ai"):
            removed.append(route.path)
        else:
            new_routes.append(route)

    app.router.routes = new_routes

    if removed:
        logger.info(f"Rotas de AI removidas da aplicação: {removed}")
    else:
        logger.info("Nenhuma rota /ai* encontrada para remover.")


# Executa a limpeza logo após registrar os routers
remove_ai_routes()


# ---------------------------
# HEALTHCHECKS / STATUS
# ---------------------------

@app.get("/", tags=["default"])
def root():
    """
    Healthcheck simples da app.
    """
    return {"ok": True, "msg": "FastAPI Platform Lab API online"}


@app.get("/health", tags=["default"])
def health():
    """
    Healthcheck leve para orquestrador / load balancer.
    Não toca no banco.
    """
    return {"status": "ok"}


@app.get("/dbstatus", tags=["default"])
def db_status(db: Session = Depends(get_db)):
    """
    Healthcheck do banco.
    Usa SELECT 1.
    Se falhar, retorna detalhe no JSON e registra no log.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return {"db": "error", "detail": str(e)}