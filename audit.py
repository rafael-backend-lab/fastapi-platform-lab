from datetime import datetime
from sqlalchemy.orm import Session

from models import AuditLog, User


def log_action(
    db: Session,
    action: str,
    detail: str | None = None,
    user: User | None = None,
    ip: str | None = None,
) -> None:
    """
    Registra uma ação no sistema.

    - action: nome do evento (ex: 'signup', 'login_failed', 'ai_prompt_moderated')
    - detail: descrição detalhada (opcional)
    - user: usuário responsável (opcional, pode ser None)
    - ip: endereço IP se houver (opcional)
    """

    log = AuditLog(
        action=action,
        detail=detail,
        user_id=user.id if user else None,
        ip=ip,
        created_at=datetime.utcnow(),
    )

    db.add(log)
    # NÃO faz commit aqui — o commit é feito no fluxo principal