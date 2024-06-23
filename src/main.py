import os
import shutil
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from src.models import (
    documents_dir,
    AsyncSessionLocal,
    Document,
    init_models,
    DocumentsText,
)
from src.tasks import extract_text_from_image, logger
from src.schemas import (
    DocumentDelete,
    ALLOWED_EXTENSIONS,
)
import logging

# Configure logger
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
logger.addHandler(handler)

# Initialize the FastAPI app with lifespan events
app = FastAPI()


# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# Initialize and shutdown app events
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_models()
        yield
    finally:
        pass


app = FastAPI(lifespan=lifespan)


@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(documents_dir, filename)

    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Add entry to the database
    new_doc = Document(path=file_path)
    db.add(new_doc)
    await db.commit()

    return JSONResponse(
        status_code=200, content={"id": new_doc.id, "path": new_doc.path}
    )


@app.delete("/doc_delete/{doc_id}", response_model=dict)
async def delete_doc(
    doc_id: int = Path(
        ...,
        title="Document ID",
        description="The ID of the document to delete",
        example=1,
    ),
    db: AsyncSession = Depends(get_db),
):

    try:
        result = await db.execute(select(Document).where(Document.id == doc_id))
        document = result.scalars().first()

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        if os.path.exists(document.path):
            os.remove(document.path)
        else:
            raise HTTPException(status_code=404, detail="File not found on disk")

        await db.delete(document)
        await db.commit()

        return JSONResponse(
            status_code=200, content={"detail": "Document deleted successfully"}
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/doc_analyse/{image_id}")
async def doc_analyse(
    image_id: int = Path(
        ..., title="Image ID", description="The ID of the image to analyze", example=1
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info(f"Received request to analyze document with image_id: {image_id}")

        result = await db.execute(select(Document).where(Document.id == image_id))
        document = result.scalars().first()

        if document is None:
            logger.error(f"Document with image_id {image_id} not found")
            raise HTTPException(status_code=404, detail="Document not found")

        task = extract_text_from_image.delay(document.path, image_id)
        logger.info(f"Task submitted: {task.id}")

        await db.commit()

        return {
            "message": "Text extraction task submitted",
            "task_id": task.id,
            "document_path": document.path,
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Error processing document analysis: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/get_text/{doc_id}")
async def get_text(doc_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Fetching document text for doc_id: {doc_id}")
        result = await db.execute(
            select(DocumentsText).where(DocumentsText.id_doc == doc_id)
        )
        document_text = result.scalars().first()

        if document_text is None:
            raise HTTPException(status_code=404, detail="Document text not found")

        await db.commit()

        return JSONResponse(status_code=200, content={"text": document_text.text})

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        await db.close()
        logger.info("Database session closed")
