# conftest.py

import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from src.main import app
from fastapi.testclient import TestClient
from httpx import AsyncClient
from dotenv import load_dotenv
from src.models import Base

# Load environment variables from .env.test file
load_dotenv(dotenv_path=".env.test")

# Retrieve database connection parameters from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# PostgreSQL connection string for the test database
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine for database operations
test_engine = create_engine(DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def check_database_exists():
    try:
        with test_engine.connect() as conn:
            sql_statement = text("SELECT 1 FROM pg_database WHERE datname=:dbname")
            result = conn.execute(sql_statement, {"dbname": DB_NAME})
            return result.fetchone() is not None
    except OperationalError:
        return False


# Fixture to create the test database if it doesn't exist
@pytest.fixture(scope="session")
def create_test_database():
    if not check_database_exists():
        conn = test_engine.connect()
        conn.execute(f"CREATE DATABASE {DB_NAME}")
        conn.close()

    Base.metadata.create_all(bind=test_engine)
    yield

    Base.metadata.drop_all(bind=test_engine)


# Fixture for creating a database session for tests
@pytest.fixture(scope="function")
def db_session(create_test_database):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# Fixture for testing with the FastAPI TestClient
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[override_get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# Fixture for testing with the Async FastAPI TestClient
@pytest.fixture(scope="function")
async def async_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[override_get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
