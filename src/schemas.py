from pydantic import BaseModel, Field

# Допустимые форматы файлов для pytesseract
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp", "gif"}


class DocumentBase(BaseModel):
    id: int


class DocumentDelete(BaseModel):
    doc_id: int = Field(..., example=1)


class DocumentAnalyse(BaseModel):
    image_id: int = Field(..., example=1)
