import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lê a URL do banco via variável de ambiente (.env)
# Se não tiver setado, cai no padrão LOCALHOST (sem Docker pra API)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/platform_lab_db",
)

# Cria o engine do SQLAlchemy (future=True para sintaxe moderna)
engine = create_engine(DATABASE_URL, future=True)

# SessionLocal: cada request cria uma sessão independente
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base para os models herdarem
Base = declarative_base()


def get_db():
    """
    Dependência padrão do FastAPI para injeção de sessão do banco.
    Garante que a conexão é aberta no início da request
    e fechada corretamente no final.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()