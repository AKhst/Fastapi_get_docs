from pydantic import BaseModel, Field

# Допустимые форматы файлов для pytesseract
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tiff", "bmp", "gif"}


class DocumentBase(BaseModel):
    id: int


class DocumentDelete(BaseModel):
    doc_id: int

    # Пример необходимо передать через json_schema_extra
    class Config:
        json_schema_extra = {"example": {"doc_id": 1}}


class DocumentAnalyse(BaseModel):
    image_id: int

    # Пример необходимо передать через json_schema_extra
    class Config:
        json_schema_extra = {"example": {"image_id": 1}}
