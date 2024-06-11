import os
import shutil
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import (
    documents_dir,
    AsyncSessionLocal,
    Document,
    init_models,
    DocumentsText,
)
from src.tasks import extract_text_from_image
from src.schemas import (
    DocumentDelete,
    DocumentAnalyse,
    ALLOWED_EXTENSIONS,
    DocumentBase,
)


# Функция для инициализации приложения при запуске
async def initialize_app():
    await init_models()


# Функция для завершения работы приложения при остановке
async def shutdown_app():
    pass  # Можно добавить необходимые действия при завершении работы приложения, если такие есть


# Контекстный менеджер для выполнения действий при старте и остановке приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await initialize_app()  # Вызываем функцию для инициализации приложения
        yield
    finally:
        await shutdown_app()  # Вызываем функцию для завершения работы приложения


# Используем контекстный менеджер для выполнения действий при старте и остановке приложения
app = FastAPI(lifespan=lifespan)


# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # Generate a unique filename
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(documents_dir, filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Add entry to the database
    new_doc = Document(path=file_path)
    db.add(new_doc)
    await db.commit()
    # await db.refresh(new_doc)

    return JSONResponse(
        status_code=200, content={"id": new_doc.id, "path": new_doc.path}
    )


@app.delete("/doc_delete")
async def delete_doc(request: DocumentDelete, db: AsyncSession = Depends(get_db)):
    doc_id = request.doc_id
    # Получение документа из базы данных по id
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalars().first()

    # Если документ не найден, возвращаем ошибку 404
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Удаление файла с диска
    if os.path.exists(document.path):
        os.remove(document.path)
    else:
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Удаление записи из базы данных
    await db.delete(document)
    await db.commit()

    return JSONResponse(
        status_code=200, content={"detail": "Document deleted successfully"}
    )


@app.post("/doc_analyse/{image_id}")
async def doc_analyse(request: DocumentAnalyse, db: AsyncSession = Depends(get_db)):
    image_id = request.image_id
    result = await db.execute(select(Document).where(Document.id == image_id))
    document = result.scalars().first()

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    task = extract_text_from_image.delay(document.path, image_id)
    return {
        "message": "Text extraction task submitted",
        "task_id": task.id,
        "document_path": document.path,
    }


@app.get("/get_text")
async def get_text(doc_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DocumentsText).where(DocumentsText.id_doc == doc_id)
    )
    document_text = result.scalars().first()

    if document_text is None:
        raise HTTPException(status_code=404, detail="Document text not found")

    return JSONResponse(status_code=200, content={"text": document_text.text})
