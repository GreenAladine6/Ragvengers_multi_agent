"""
Vector similarity search using pgvector
"""

import logging
from typing import List, Dict, Any

from database.connection import db_manager
from database.models import ReportChunk
from database.chroma_client import query as chroma_query, get_client as get_chroma_client

logger = logging.getLogger(__name__)

class VectorRetriever:
    """Retrieves relevant chunks using vector similarity"""
    
    def __init__(self, embedder, top_k: int = 5):
        self.embedder = embedder
        self.top_k = top_k
        
    async def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant chunks for a query using vector similarity
        """
        if top_k:
            self.top_k = top_k
        
        try:
            # Generate embedding for query
            query_embedding = await self.embedder.generate_embedding(query)
            
            # Convert to PostgreSQL vector format
            embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
            
            session = db_manager.get_session()
            
            try:
                # Query Chroma for nearest neighbors
                client = get_chroma_client()
                if not client:
                    logger.error('Chroma client not initialized')
                    return []

                results = chroma_query(query_embedding, n_results=self.top_k)

                chunks = []
                for item in results:
                    meta = item.get('metadata', {})
                    dist = item.get('distance', 0)
                    # Approximate similarity from distance (not exact)
                    similarity = max(0.0, 1.0 - float(dist))
                    chunks.append({
                        'id': item.get('id'),
                        'text': item.get('text'),
                        'section': meta.get('section', 'unknown'),
                        'repo_url': meta.get('repo_url'),
                        'features_count': meta.get('features_count', 0),
                        'rules_count': meta.get('rules_count', 0),
                        'similarity': similarity
                    })
                
                logger.info(f"Retrieved {len(chunks)} chunks for query")
                return chunks
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return []
    
    async def hybrid_search(self, query: str, keywords: List[str] = None) -> List[Dict]:
        """
        Hybrid search combining vector similarity with keyword matching
        """
        # Get vector results
        vector_results = await self.retrieve(query, top_k=10)
        
        if not keywords or not vector_results:
            return vector_results[:self.top_k]
        
        # Boost scores for chunks containing keywords
        for chunk in vector_results:
            boost = 0
            for keyword in keywords:
                if keyword.lower() in chunk['text'].lower():
                    boost += 0.1
            chunk['similarity'] = min(1.0, chunk['similarity'] + boost)
        
        # Re-sort by boosted similarity
        vector_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return vector_results[:self.top_k]
