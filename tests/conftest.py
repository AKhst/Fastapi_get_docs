import os
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from src.main import app, get_db
from src.models import Base, init_models
from src.utils import cleanup_directory, create_test_file
from celery import Celery
from celery.contrib.testing.worker import start_worker
from src.tasks import celery as celery_tasks

load_dotenv("/Users/admin/PycharmProjects/Fastapi_get_docs/.test.env")

# Проверка наличия всех необходимых переменных окружения
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# PostgreSQL's connection string for the test database
connection_string = (
    f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

# Create SQLAlchemy async_engine for database operations
async_engine = create_async_engine(connection_string, echo=True)

# Database session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)
test_documents_dir = "/Users/admin/PycharmProjects/Fastapi_get_docs/test_documents"

# Создание тестового файла
file_path = create_test_file("test_file.txt", test_documents_dir)
print(f"Created file: {file_path}")

# Удаление содержимого директории после использования
cleanup_directory(test_documents_dir)
print(f"Cleaned up directory: {test_documents_dir}")


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": os.getenv("CELERY_BROKER_URL"),
        "result_backend": os.getenv("CELERY_RESULT_BACKEND"),
    }


@pytest.fixture(scope="session")
def celery_includes():
    return ["src.tasks"]  # замените на ваш модуль с задачами Celery


@pytest.fixture(scope="session")
def celery_app(celery_config, celery_includes):
    app = Celery(
        "tasks",
        broker=celery_config["broker_url"],
        backend=celery_config["result_backend"],
    )
    app.conf.update(celery_config)
    app.conf.update(
        task_always_eager=True
    )  # Запускаем задачи синхронно в тестовом режиме
    app.autodiscover_tasks(celery_includes)

    # Регистрируем стандартные задачи, включая ping
    app.register_task(app.tasks["celery.ping"])

    print(
        f"Tasks registered: {app.tasks.keys()}"
    )  # Вывод всех зарегистрированных задач
    return app


@pytest.fixture()
def celery_worker(celery_app):
    with start_worker(celery_app, ping_task=True) as worker:
        yield worker


# Ваши остальные фикстуры


@pytest.fixture(scope="function")
async def db():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def initialize_test_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await init_models()  # Ensure all models are initialized


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_files():
    # Create test files before each test
    os.makedirs(test_documents_dir, exist_ok=True)
    yield
    # Remove test files after each test
    cleanup_directory(test_documents_dir)


@pytest.fixture(scope="function")
async def async_client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


print(f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
