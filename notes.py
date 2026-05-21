from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db
from models import Note, User
from schemas import NoteCreate, NoteOut, NoteList
from auth import get_current_user
from audit_log import log_action  # <-- AQUI ESTAVA O ERRO: era "from audit import log_action"

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=NoteList)
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lista todas as notas do usuário autenticado.
    - Protegido por JWT (usa get_current_user).
    - Retorna em ordem da mais recente para a mais antiga.
    """
    notes = (
        db.query(Note)
        .filter(Note.owner_id == current_user.id)
        .order_by(Note.created_at.desc())
        .all()
    )

    return {"notes": notes}


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Cria uma nova nota vinculada ao usuário autenticado.
    - Valida se o texto não é vazio.
    - Salva a nota no banco.
    - Registra auditoria da criação da nota.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Texto da nota não pode ser vazio.",
        )

    note = Note(
        text=text,
        owner_id=current_user.id,
    )

    db.add(note)
    db.flush()  # garante ID da nota para o log

    # registra auditoria (não comita aqui)
    log_action(
        db=db,
        action="note_created",
        detail=f"Nota criada (id={note.id}) pelo usuário id={current_user.id}",
        user=current_user,
    )

    # persiste nota + log juntos
    db.commit()
    db.refresh(note)

    return note