import os
from datetime import datetime, timezone

import timestamp
from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import async_engine

# Настройки
documents_dir = "/Users/admin/PycharmProjects/Fastapi_get_docs/documents"

os.makedirs(documents_dir, exist_ok=True)

# Database session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "document"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    text = relationship("DocumentsText", cascade="all, delete", backref="document")


class DocumentsText(Base):
    __tablename__ = "documents_text"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_doc: Mapped[int] = mapped_column(
        ForeignKey("document.id", ondelete="CASCADE"), unique=True
    )
    text: Mapped[str]


# Создание таблиц
async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
