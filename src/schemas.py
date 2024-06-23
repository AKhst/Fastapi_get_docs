from fastapi import Path
from typing import Annotated
from pydantic import BaseModel

# Допустимые форматы файлов для pytesseract
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp", "gif"}


class DocumentBase(BaseModel):
    id: int


class DocumentDelete(BaseModel):
    doc_id: Annotated[
        int,
        Path(title="Document ID", description="The ID of the document to delete", ge=1),
    ]
