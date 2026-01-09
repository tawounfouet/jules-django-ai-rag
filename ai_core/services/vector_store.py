import chromadb
from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT
        )
        self.embedding_fn = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )

    def get_collection_name(self, company_id, knowledge_base_id):
        # Naming convention: kb_{company_id}_{knowledge_base_id}
        # IDs are likely integers or UUIDs.
        return f"kb_{company_id}_{knowledge_base_id}"

    def get_or_create_collection(self, company_id, knowledge_base_id):
        name = self.get_collection_name(company_id, knowledge_base_id)
        # We need a custom embedding function adapter for Chroma if we pass it directly,
        # or we generate embeddings manually and pass them.
        # LangChain's Chroma wrapper is easier, but here we are using raw client potentially.
        # Let's use the raw client for explicit control as per requirements,
        # but we need to generate embeddings.

        # Actually, it's often easier to use LangChain's Chroma wrapper if we want to integrate with the RAG pipeline later.
        # However, for ingestion, we want strict control.

        return self.client.get_or_create_collection(name=name)

    def add_documents(self, company_id, knowledge_base_id, texts, metadatas, ids=None):
        collection = self.get_or_create_collection(company_id, knowledge_base_id)

        # Generate embeddings
        embeddings = self.embedding_fn.embed_documents(texts)

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]

        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        return len(ids)

    def search(self, company_id, knowledge_base_id, query, k=3):
        collection = self.get_or_create_collection(company_id, knowledge_base_id)
        query_embedding = self.embedding_fn.embed_query(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        return results

    @staticmethod
    def chunk_text(text, chunk_size=1000, chunk_overlap=200):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_text(text)
