"""
Simple Chroma DB client wrapper for storing and querying embeddings
"""
import os
from typing import List, Dict, Any

try:
    import chromadb
    from chromadb.config import Settings
except Exception:
    chromadb = None


class ChromaClient:
    def __init__(self, persist_directory: str | None = None, collection_name: str | None = None):
        if not chromadb:
            raise ImportError("Please install chromadb: pip install chromadb")

        persist_dir = persist_directory or os.getenv('CHROMA_PERSIST_DIR')
        settings = Settings(persist_directory=persist_dir) if persist_dir else Settings()
        self.client = chromadb.Client(settings)
        self.collection_name = collection_name or os.getenv('CHROMA_COLLECTION', 'report_chunks')

        try:
            self.collection = self.client.get_collection(self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(self.collection_name)

    def upsert(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        """Upsert embeddings into the Chroma collection"""
        self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def query(self, embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the collection and return list of items with id, document, metadata and distance"""
        result = self.collection.query(query_embeddings=[embedding], n_results=n_results, include=['metadatas', 'documents', 'distances'])
        items = []
        # result fields are lists-of-lists (batch support); take first batch
        ids = result.get('ids', [[]])[0]
        docs = result.get('documents', [[]])[0]
        metas = result.get('metadatas', [[]])[0]
        dists = result.get('distances', [[]])[0]

        for idx, doc, meta, dist in zip(ids, docs, metas, dists):
            items.append({
                'id': idx,
                'text': doc,
                'metadata': meta,
                'distance': dist
            })

        return items


# Lazy singleton
_client: ChromaClient | None = None


def get_client() -> ChromaClient | None:
    global _client
    if _client:
        return _client
    try:
        # Default to a local persistence directory if not provided
        persist_dir = os.getenv('CHROMA_PERSIST_DIR') or os.path.join(os.getcwd(), '.chromadb')
        _client = ChromaClient(persist_directory=persist_dir)
        return _client
    except Exception:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Failed to initialize Chroma client')
        return None


def upsert(ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
    c = get_client()
    if not c:
        raise RuntimeError('Chroma client not available')
    c.upsert(ids, embeddings, metadatas, documents)


def query(embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
    c = get_client()
    if not c:
        raise RuntimeError('Chroma client not available')
    return c.query(embedding, n_results=n_results)
