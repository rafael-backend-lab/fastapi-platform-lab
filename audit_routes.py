from typing import Any, List, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import get_db
from models import User
from auth import get_current_user
from audit_log import log_action  # registra auditoria da análise


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


class PromptIn(BaseModel):
    prompt: str


class SafetyCheckResult(BaseModel):
    prompt: str
    blocked: bool
    risk_score: float
    risk_level: str
    reasons: List[str]


# Palavras-chave sensíveis (versão inicial, simples)
SENSITIVE_KEYWORDS = {
    "violence": [
        "matar",
        "assassinar",
        "estrangular",
        "bomba",
        "explosivo",
        "tiro",
        "tiroteio",
    ],
    "self_harm": [
        "me matar",
        "me suicidar",
        "suicídio",
        "tirar minha vida",
    ],
    "illegal": [
        "tráfico",
        "falsificar",
        "clonar cartão",
        "droga",
        "cocaína",
        "armas ilegais",
    ],
    "sexual": [
        "pornografia infantil",
        "pedofilia",
        "estupro",
    ],
}


def analyze_prompt(prompt: str) -> Tuple[float, List[str]]:
    """
    Análise simples de risco com base em palavras-chave.

    Retorna:
    - score (0.0 a 1.0)
    - lista de categorias ativadas (violence, illegal, etc.)
    """
    text = prompt.lower()
    reasons: List[str] = []
    score = 0.0

    for category, words in SENSITIVE_KEYWORDS.items():
        for w in words:
            if w in text:
                reasons.append(category)
                # cada categoria encontrada soma 0.3 de risco
                score += 0.3
                break

    if score > 1.0:
        score = 1.0

    return score, reasons


def risk_level(score: float) -> str:
    """
    Converte o score numérico em nível de risco.
    """
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


@router.post(
    "/moderate",
    response_model=SafetyCheckResult,
    status_code=status.HTTP_200_OK,
)
def moderate_prompt(
    payload: PromptIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Endpoint de moderação de prompt de IA.

    - Recebe um texto (prompt).
    - Analisa risco com base em palavras-chave sensíveis.
    - Classifica em low / medium / high.
    - Se high, marca como blocked=True.
    - Registra auditoria da análise (ai_prompt_moderated).
    """
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt não pode ser vazio.",
        )

    score, reasons = analyze_prompt(prompt)
    level = risk_level(score)
    blocked = level == "high"

    # registra auditoria no mesmo contexto de transação
    log_action(
        db=db,
        action="ai_prompt_moderated",
        detail=(
            f"prompt moderado (level={level}, score={score:.2f}, "
            f"blocked={blocked}, reasons={reasons})"
        ),
        user=current_user,
    )
    db.commit()

    return SafetyCheckResult(
        prompt=prompt,
        blocked=blocked,
        risk_score=score,
        risk_level=level,
        reasons=reasons,
    )