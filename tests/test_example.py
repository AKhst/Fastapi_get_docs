# tests/test_example.py
import os
import uuid
import pytest
import mimetypes
from httpx import AsyncClient, ASGITransport
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from .conftest import test_documents_dir
from src.main import app, get_db
from src.models import Document, DocumentsText
from src.utils import create_test_file


@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_upload_doc(db: AsyncSession, initialize_test_database):
    file_path = create_test_file("test_image.png", test_documents_dir)

    async for session in get_db():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            with open(file_path, "rb") as file:
                # Determine content type and validate file type
                file_type, _ = mimetypes.guess_type(file_path)
                assert (
                    file_type == "image/png"
                ), "Uploaded file must be of type image/png"

                files = {"file": ("test_image.png", file, file_type)}
                response = await ac.post("/upload_doc", files=files)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Use session context manager to interact with database
        async with session.begin():
            document = await session.get(Document, data["id"])

        assert document is not None
        assert document.path == data["path"]
        assert os.path.exists(document.path)

        # Extract file name from path and check if it matches expected pattern
        file_name_from_path = os.path.basename(document.path)
        uuid_str = file_name_from_path.split(".")[0]  # Remove file extension
        try:
            uuid.UUID(uuid_str, version=4)  # Check if uuid_str is a valid UUID4
        except ValueError:
            pytest.fail(f"Invalid UUID format: {uuid_str}")


@pytest.mark.asyncio
async def test_delete_doc(db: AsyncSession, initialize_test_database):
    # Создаем тестовый файл для загрузки
    file_path = create_test_file("test_image_to_delete.png", test_documents_dir)

    async for session in get_db():
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            with open(file_path, "rb") as file:
                file_type, _ = mimetypes.guess_type(file_path)
                files = {"file": ("test_image_to_delete.png", file, file_type)}
                upload_response = await ac.post("/upload_doc", files=files)

            assert upload_response.status_code == status.HTTP_200_OK
            data = upload_response.json()

            doc_id = data["id"]

            # Now delete the uploaded document
            delete_response = await ac.delete(f"/doc_delete/{doc_id}")

            assert delete_response.status_code == status.HTTP_200_OK
            delete_data = delete_response.json()
            assert delete_data["detail"] == "Document deleted successfully"

            # Verify the document is deleted from the database
            async with session.begin():
                deleted_document = await session.get(Document, doc_id)

            assert deleted_document is None

            # Verify the file is deleted from the disk
            assert not os.path.exists(data["path"])
