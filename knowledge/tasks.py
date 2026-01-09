import logging
import traceback
from celery import shared_task
from django.db import transaction
from .models import File, EmbeddingStatus, IngestionLog
from .services.parsers import DocumentParser
from ai_core.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def ingest_file(self, file_id):
    try:
        file_obj = File.objects.get(id=file_id)

        # Create or Get status
        status, created = EmbeddingStatus.objects.get_or_create(file=file_obj)
        status.statut = 'processing'
        status.save()

        # 1. Parse
        if not file_obj.fichier_physique:
            raise ValueError("No physical file found.")

        # We need to open the file. Since it's a FileField, we can access it.
        # Ensure file is open
        with file_obj.fichier_physique.open('rb') as f:
            text_content = DocumentParser.extract_text(f, file_obj.type)

        if not text_content.strip():
            raise ValueError("Extracted text is empty.")

        # 2. Chunk
        chunks = VectorStoreService.chunk_text(text_content)

        # 3. Embed & Store
        vector_store = VectorStoreService()
        kb = file_obj.source.knowledge_base
        company_id = kb.company.id
        kb_id = kb.id

        metadatas = []
        for i, chunk in enumerate(chunks):
            meta = {
                "company_id": company_id,
                "knowledge_base_id": kb_id,
                "file_id": file_obj.id,
                "chunk_index": i,
                "source_nom": file_obj.source.nom,
                "title": file_obj.titre
            }
            # Add existing file metadata if any
            if file_obj.metadata:
                 # Ensure values are simple types for Chroma
                 for k, v in file_obj.metadata.items():
                     if isinstance(v, (str, int, float, bool)):
                         meta[k] = v
            metadatas.append(meta)

        vector_store.add_documents(
            company_id=company_id,
            knowledge_base_id=kb_id,
            texts=chunks,
            metadatas=metadatas
        )

        # 4. Update Status
        status.statut = 'completed'
        status.nombre_de_chunks = len(chunks)
        status.collection_chroma_id = vector_store.get_collection_name(company_id, kb_id)
        status.save()

        # Update KnowledgeBase doc count (approximate or explicit)
        kb.nombre_documents += 1
        kb.save()

        # Log success
        IngestionLog.objects.create(
            file=file_obj,
            logs=f"Successfully ingested {len(chunks)} chunks.",
            succes=True
        )

    except Exception as e:
        # Log failure
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"Ingestion failed for file {file_id}: {error_msg}")

        try:
            status = EmbeddingStatus.objects.get(file_id=file_id)
            status.statut = 'failed'
            status.save()

            IngestionLog.objects.create(
                file=File.objects.get(id=file_id), # re-fetch to be safe
                logs=error_msg,
                succes=False
            )
        except Exception as inner_e:
            logger.error(f"Failed to log error for file {file_id}: {inner_e}")
