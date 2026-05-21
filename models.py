from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Admin flag:
    # - False (padrão) para usuários comuns
    # - True para administradores (primeiro usuário criado, etc.)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Relacionamentos
    notes = relationship(
        "Note",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship(
        "User",
        back_populates="notes",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)      # Ex: signup, login_success, note_created
    detail = Column(String, nullable=True)       # Ex: "User created: rafael"
    ip = Column(String, nullable=True)           # Futuro: pegar IP real se quiser
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="audit_logs",
    )