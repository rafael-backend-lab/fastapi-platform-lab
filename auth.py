from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db import get_db
from models import User
from schemas import UserCreate, UserOut, Token
from security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)
from audit_log import log_action   # <-- IMPORT CORRETO, SEM IMPORT CIRCULAR

router = APIRouter()

# OAuth2PasswordBearer:
# Usado pelo Swagger (Authorize) no fluxo password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Decodifica o token JWT, valida e retorna o usuário.
    """
    payload = decode_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário com hashing de senha e auditoria.
    """
    # Verifica se username ou email já existem
    existing_user = (
        db.query(User)
        .filter(
            (User.username == user_in.username)
            | (User.email == user_in.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ou email já está em uso.",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )

    db.add(user)

    # Auditoria (na MESMA transação)
    log_action(
        db=db,
        action="signup",
        detail=f"Usuário criado: {user.username}",
        user=user,
    )

    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login padrão (OAuth2 Password Flow).
    """
    username = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.username == username).first()

    # Falha no login
    if not user or not verify_password(password, user.hashed_password):
        log_action(
            db=db,
            action="login_failed",
            detail=f"Tentativa de login falhou para username={username}",
            user=None,
        )
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Sucesso → gerar token
    access_token = create_access_token({"sub": str(user.id)})

    # Auditoria
    log_action(
        db=db,
        action="login_success",
        detail=f"Login bem-sucedido para username={user.username}",
        user=user,
    )
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """
    Retorna o usuário autenticado.
    """
    return current_user