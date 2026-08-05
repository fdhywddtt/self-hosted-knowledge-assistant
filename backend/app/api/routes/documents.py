from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, verify_admin_api_key, verify_api_key
from app.db.models import Document
from app.schemas.document import DocumentListResponse, DocumentRead, UploadResponse
from app.services.ingestion import ingest_document, save_upload

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(verify_api_key)])
async def upload_document(
    file: UploadFile = File(...),
    background: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")

    filename = file.filename or "unnamed"
    try:
        _, storage_path = save_upload(data, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = Document(
        filename=filename,
        content_type=file.content_type or "application/octet-stream",
        status="uploaded",
        storage_path=storage_path,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    background.add_task(ingest_document, document.id)
    return UploadResponse(id=document.id, filename=document.filename, status=document.status)


@router.get("", response_model=DocumentListResponse, dependencies=[Depends(verify_api_key)])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return DocumentListResponse(items=list(result.scalars().all()))


@router.get("/{document_id}", response_model=DocumentRead, dependencies=[Depends(verify_api_key)])
async def get_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@router.delete("/{document_id}", dependencies=[Depends(verify_admin_api_key)])
async def delete_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="文档不存在")
    await db.delete(document)
    await db.commit()
    return {"deleted": True}
