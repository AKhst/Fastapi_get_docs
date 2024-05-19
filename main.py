import os
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()


# API эндпоинты
@app.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...)):
    file_path = os.path.join(DOCUMENTS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()
    new_doc = Document(filename=file.filename)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    db.close()

    return JSONResponse(content={"id": new_doc.id, "filename": new_doc.filename})


@app.delete("/doc_delete")
async def doc_delete(doc_id: int):
    db = SessionLocal()
    doc = db.query(Document).get(doc_id)
    if doc:
        file_path = os.path.join(DOCUMENTS_DIR, doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete(doc)
        db.commit()
        db.close()
        return JSONResponse(content={"message": "Document deleted"})
    else:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")


@app.post("/doc_analyse")
async def doc_analyse(doc_id: int):
    db = SessionLocal()
    doc = db.query(Document).get(doc_id)
    if doc:
        file_path = os.path.join(DOCUMENTS_DIR, doc.filename)
        process_document.delay(doc_id, file_path)
        db.close()
        return JSONResponse(content={"message": "Document processing started"})
    else:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")


@app.get("/get_text")
async def get_text(doc_id: int):
    db = SessionLocal()
    doc = db.query(Document).get(doc_id)
    if doc:
        db.close()
        return JSONResponse(content={"id": doc.id, "text": doc.text})
    else:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")
