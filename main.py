import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import uuid
from models import documents_dir, AsyncSessionLocal, Document, init_models

app = FastAPI()


# Функция, которая будет вызвана при запуске приложения
@app.on_event("startup")
async def startup_event():
    await init_models()


# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # Generate a unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(documents_dir, filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Add entry to the database
    new_doc = Document(path=file_path)
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    return JSONResponse(
        status_code=200, content={"id": new_doc.id, "path": new_doc.path}
    )
