from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# =========================
# USERS
# =========================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserOut(UserBase):
    id: int
    created_at: datetime
    is_admin: bool

    class Config:
        from_attributes = True  # compatível com SQLAlchemy (Pydantic v2)


# =========================
# LOGIN / AUTH
# =========================

class LoginIn(BaseModel):
    """
    Usado pelo /login no auth.py
    """
    username: str
    password: str


# Mantém o nome antigo como compatibilidade, se algum arquivo ainda usar `Login`
class Login(LoginIn):
    """
    Alias de LoginIn (caso alguma parte antiga ainda use Login).
    """
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================
# NOTES
# =========================

class NoteBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class NoteCreate(NoteBase):
    pass


class NoteOut(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class NoteList(BaseModel):
    notes: List[NoteOut]


# =========================
# AUDIT LOGS
# =========================

class AuditLogOut(BaseModel):
    id: int
    action: str
    detail: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogList(BaseModel):
    logs: List[AuditLogOut]