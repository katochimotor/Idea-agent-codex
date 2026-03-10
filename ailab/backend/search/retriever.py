from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from backend.models.document_model import Document, DocumentChunk
from backend.models.model_registry_model import ModelRegistryEntry
from backend.models.run_model import PipelineRun
from backend.models.vector_model import VectorCollection, VectorEntry, VectorSyncRun
from backend.search.embedding_service import LocalEmbeddingService
from backend.search.vector_index import LocalVectorIndex
from backend.utils.slug_generator import slugify


class VectorSearchService:
    def __init__(self) -> None:
        self.embedding_service = LocalEmbeddingService()
        self.index = LocalVectorIndex()

    def _now(self) -> str:
        return datetime.utcnow().isoformat()

    def _ensure_embedding_model(self, session: Session) -> ModelRegistryEntry:
        model = session.exec(
            select(ModelRegistryEntry)
            .where(ModelRegistryEntry.task_key == "embeddings")
            .where(ModelRegistryEntry.enabled == True)  # noqa: E712
            .order_by(ModelRegistryEntry.is_default.desc(), ModelRegistryEntry.id.desc())
        ).first()
        if model:
            return model

        now = self._now()
        model = ModelRegistryEntry(
            task_key="embeddings",
            provider="local",
            model_name="local-hash-embeddings-v1",
            endpoint_type="embeddings",
            input_mode="text",
            output_schema_json=None,
            temperature=None,
            max_tokens=None,
            embedding_dimensions=self.embedding_service.dimensions,
            is_default=True,
            enabled=True,
            fallback_model_id=None,
            config_json=None,
            created_at=now,
            updated_at=now,
        )
        session.add(model)
        session.flush()
        return model

    def ensure_collection(self, session: Session, collection_key: str = "document_chunks_default") -> VectorCollection:
        collection = session.exec(
            select(VectorCollection).where(VectorCollection.collection_key == collection_key)
        ).first()
        if collection:
            return collection

        now = self._now()
        model = self._ensure_embedding_model(session)
        collection = VectorCollection(
            collection_key=collection_key,
            entity_type="document_chunk",
            embedding_model_id=model.id,
            dimensions=model.embedding_dimensions or self.embedding_service.dimensions,
            metric="cosine",
            index_path=str(self.index._path(collection_key)),
            metadata_json=None,
            created_at=now,
            updated_at=now,
        )
        session.add(collection)
        session.flush()
        return collection

    def ensure_document_chunks(self, session: Session, document: Document, chunk_size: int = 320, overlap: int = 60) -> list[DocumentChunk]:
        existing = session.exec(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index.asc())
        ).all()
        if existing:
            return existing

        content = document.content_text.strip()
        if not content:
            return []

        step = max(chunk_size - overlap, 1)
        chunks: list[DocumentChunk] = []
        now = self._now()
        for index, start in enumerate(range(0, len(content), step)):
            chunk_text = content[start : start + chunk_size]
            if not chunk_text:
                continue
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                chunk_text=chunk_text,
                token_count=len(chunk_text.split()),
                char_start=start,
                char_end=start + len(chunk_text),
                content_hash=slugify(f"{document.id}-{index}-{len(chunk_text)}"),
                metadata_json=None,
                created_at=now,
            )
            session.add(chunk)
            session.flush()
            chunks.append(chunk)
        return chunks

    def rebuild_document_chunk_index(self, session: Session, pipeline_run: PipelineRun | None = None) -> dict:
        collection = self.ensure_collection(session)
        documents = session.exec(
            select(Document).where(Document.status == "active").order_by(Document.id.asc())
        ).all()

        now = self._now()
        sync_run = VectorSyncRun(
            collection_id=collection.id,
            pipeline_run_id=pipeline_run.id if pipeline_run else None,
            status="running",
            inserted_count=0,
            updated_count=0,
            deleted_count=0,
            error_message=None,
            created_at=now,
            updated_at=now,
        )
        session.add(sync_run)
        session.flush()

        vectors_to_upsert: dict[str, list[float]] = {}
        inserted_count = 0
        updated_count = 0

        for document in documents:
            chunks = self.ensure_document_chunks(session, document)
            for chunk in chunks:
                vector_key = f"document_chunk:{chunk.id}:v1"
                vector = self.embedding_service.embed(chunk.chunk_text)
                existing = session.exec(
                    select(VectorEntry)
                    .where(VectorEntry.collection_id == collection.id)
                    .where(VectorEntry.entity_type == "document_chunk")
                    .where(VectorEntry.entity_id == chunk.id)
                    .where(VectorEntry.version == 1)
                ).first()
                if existing:
                    existing.vector_hash = slugify(f"{chunk.content_hash}-{len(chunk.chunk_text)}")
                    existing.updated_at = now
                    updated_count += 1
                else:
                    session.add(
                        VectorEntry(
                            collection_id=collection.id,
                            entity_id=chunk.id,
                            entity_type="document_chunk",
                            vector_key=vector_key,
                            vector_hash=slugify(f"{chunk.content_hash}-{len(chunk.chunk_text)}"),
                            version=1,
                            metadata_json=None,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    inserted_count += 1
                vectors_to_upsert[vector_key] = vector

        if vectors_to_upsert:
            self.index.upsert_many(collection.collection_key, vectors_to_upsert)

        collection.updated_at = now
        sync_run.status = "completed"
        sync_run.inserted_count = inserted_count
        sync_run.updated_count = updated_count
        sync_run.updated_at = now
        session.commit()

        return {
            "collection_key": collection.collection_key,
            "documents_indexed": len(documents),
            "inserted_vectors": inserted_count,
            "updated_vectors": updated_count,
            "sync_run_id": sync_run.id,
        }

    def search_documents(self, session: Session, query: str, top_k: int = 5) -> list[dict]:
        collection = self.ensure_collection(session)
        if not session.exec(select(VectorEntry).where(VectorEntry.collection_id == collection.id)).first():
            self.rebuild_document_chunk_index(session)

        query_vector = self.embedding_service.embed(query)
        ranked = self.index.query(collection.collection_key, query_vector, top_k=top_k)

        results: list[dict] = []
        for item in ranked:
            vector_entry = session.exec(
                select(VectorEntry).where(VectorEntry.vector_key == item["vector_key"])
            ).first()
            if not vector_entry:
                continue
            chunk = session.get(DocumentChunk, vector_entry.entity_id)
            if not chunk:
                continue
            document = session.get(Document, chunk.document_id)
            if not document:
                continue
            results.append(
                {
                    "score": round(item["score"], 4),
                    "document_id": document.id,
                    "document_title": document.title,
                    "canonical_url": document.canonical_url,
                    "chunk_id": chunk.id,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                }
            )
        return results
