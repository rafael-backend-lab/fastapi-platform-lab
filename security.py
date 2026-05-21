from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import os

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv


# Carrega variáveis do arquivo .env (apenas uma vez)
load_dotenv()

# Lê valores das variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "DEV-UNSAFE-DEFAULT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Configuração do hash de senha (seguro e sem frescura de 72 bytes)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Gera o hash seguro da senha do usuário.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara a senha digitada com o hash salvo no banco.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict,
    expires_delta: Optional[int] = None,
) -> str:
    """
    Gera um JWT de acesso.
    - data: payload base (ex: {"sub": user_id})
    - expires_delta: minutos até expirar (opcional)
    """
    to_encode = data.copy()

    minutes = expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> Dict:
    """
    Valida e decodifica o JWT.
    - Se expirado ou inválido → levanta HTTP 401.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )