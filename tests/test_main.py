import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.models import Base, Document, DocumentsText, init_models

# URL для тестовой базы данных SQLite в памяти
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем асинхронный engine для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем sessionmaker для асинхронной сессии
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


# Фикстура для подготовки базы данных перед тестами
@pytest.fixture(scope="module", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Тест для проверки работы эндпоинта FastAPI
@pytest.mark.asyncio
async def test_read_main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "<!DOCTYPE html>" in response.text  # Пример проверки HTML-содержимого
