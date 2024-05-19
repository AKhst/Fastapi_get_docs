from datetime import datetime
from sqlalchemy import create_engine, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os
from celery import Celery
from config import connection_string

# Настройки
documents_dir = "documents"
os.makedirs(documents_dir, exist_ok=True)

# Настройка базы данных
async_engine = create_async_engine(connection_string, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "document"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
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


import asyncio

asyncio.run(init_models())

# Настройка Celery
celery_app = Celery("tasks", broker="pyamqp://guest@localhost//", backend="rpc://")
