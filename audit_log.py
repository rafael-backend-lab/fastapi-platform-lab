from typing import Optional
from sqlalchemy.orm import Session

from models import AuditLog, User


def log_action(
    db: Session,
    action: str,
    detail: Optional[str] = None,
    user: Optional[User] = None,
    ip: Optional[str] = None,
) -> None:
    """
    Registra uma ação de auditoria na tabela audit_logs.
    """
    log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        detail=detail,
        ip=ip,
    )

    db.add(log)
    # Não damos commit aqui.
    # O commit é responsabilidade da rota.