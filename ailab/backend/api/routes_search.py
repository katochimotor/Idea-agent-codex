from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.database.db import get_session
from backend.search.retriever import VectorSearchService


class SearchDocumentsRequest(BaseModel):
    query: str
    top_k: int = 5


router = APIRouter(prefix="/search", tags=["search"])
search_service = VectorSearchService()


@router.post("/documents")
def search_documents(payload: SearchDocumentsRequest, session: Session = Depends(get_session)):
    return search_service.search_documents(session, payload.query, top_k=payload.top_k)


@router.post("/documents/rebuild")
def rebuild_document_index(session: Session = Depends(get_session)):
    return search_service.rebuild_document_chunk_index(session)
