from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from models import User
from auth import get_current_user
from schemas import UserOut

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


# ---------------------------
#  LISTAR TODOS OS USUÁRIOS
# ---------------------------
@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lista todos os usuários do sistema.
    Acesso exclusivo para administradores (is_admin=True).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )

    users = (
        db.query(User)
        .order_by(User.id.asc())
        .all()
    )

    return users


# ---------------------------
#  PROMOVER USUÁRIO PARA ADMIN
# ---------------------------
@router.post("/promote/{user_id}", response_model=UserOut)
def promote_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Promove um usuário comum para administrador.
    Apenas administradores podem executar isso.
    """

    # Garante que só admin consegue chamar
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem promover usuários.",
        )

    # Busca o usuário que será promovido
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com ID {user_id} não encontrado.",
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já é administrador.",
        )

    # Promove o usuário
    user.is_admin = True
    db.commit()
    db.refresh(user)

    return user