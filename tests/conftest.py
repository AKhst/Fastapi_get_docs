import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from src.main import app, get_db
from src.models import Base, init_models
from src.utils import cleanup_directory, create_test_file

# Load environment variables
load_dotenv("/Users/admin/PycharmProjects/Fastapi_get_docs/.test.env")

# Get environment variables
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")
celery_broker_url = os.getenv("CELERY_BROKER_URL")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
tessdata_prefix = os.getenv("TESSDATA_PREFIX")

# Define paths
base_dir = Path(__file__).resolve().parent
test_documents_dir = base_dir / "test_documents"

# Create connection string for asynchronous connection
connection_string = (
    f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

# Create SQLAlchemy async_engine for database operations
async_engine = create_async_engine(connection_string, echo=True)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def initialize_test_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await init_models()  # Ensure all models are initialized
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db(initialize_test_database):
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_files():
    # Create test files before each test
    test_documents_dir.mkdir(parents=True, exist_ok=True)
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


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Create a test file
file_path = create_test_file("test_file.txt", test_documents_dir)
print(f"Created file: {file_path}")

# Cleanup the directory after use
cleanup_directory(test_documents_dir)
print(f"Cleaned up directory: {test_documents_dir}")
print(connection_string)
