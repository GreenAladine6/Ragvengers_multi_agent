"""
Gemini embedding generation for reports
"""

import os
import logging
from typing import List, Dict, Any
import asyncio

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from database.connection import db_manager
from database.models import Report, ReportChunk
from processor.chunker import ReportChunker
from database.chroma_client import get_client, upsert

logger = logging.getLogger(__name__)

class GeminiEmbedder:
    """Generates embeddings using Gemini API"""
    
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment")
            raise ValueError("GEMINI_API_KEY is required")
        
        if not genai:
            logger.error("google-generativeai package not installed")
            raise ImportError("Please install: pip install google-generativeai")
        
        genai.configure(api_key=api_key)
        self.model = 'models/embedding-001'
        self.chunker = ReportChunker()
        logger.info("✅ Gemini Embedder initialized")
        
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        """
        embeddings = []
        for i, text in enumerate(texts):
            if (i + 1) % 10 == 0:
                logger.info(f"Generating embeddings: {i + 1}/{len(texts)}")
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
            # Small delay to avoid rate limits
            await asyncio.sleep(0.1)
        return embeddings
    
    async def process_report(self, 
                           report_text: str, 
                           repo_url: str, 
                           metadata: Dict = None) -> str:
        """
        Process a full report: chunk, generate embeddings, store in DB
        """
        session = db_manager.get_session()
        
        try:
            logger.info(f"Processing report from {repo_url}...")
            
            # Create report record
            report = Report(
                repo_url=repo_url,
                report_text=report_text,
                features_count=metadata.get('features_count', 0) if metadata else 0,
                rules_count=metadata.get('rules_count', 0) if metadata else 0,
                files_analyzed=metadata.get('files_analyzed', []) if metadata else [],
                report_metadata=metadata or {}
            )
            session.add(report)
            session.flush()  # Get report ID
            
            # Extract metadata from text if not provided
            if not metadata:
                metadata = self.chunker.extract_metadata(report_text)
                report.features_count = metadata.get('features_count', 0)
                report.rules_count = metadata.get('rules_count', 0)
                report.files_analyzed = metadata.get('files_analyzed', [])
            
            # Chunk the report
            chunks = self.chunker.chunk_report(report_text)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Generate embeddings for chunks
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = await self.generate_embeddings_batch(chunk_texts)
            
            # Store chunks (without embedding) and collect data for Chroma upsert
            chunk_ids = []
            docs = []
            metas = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                report_chunk = ReportChunk(
                    report_id=report.id,
                    chunk_text=chunk['text'],
                    chunk_index=i,
                    section=chunk.get('section', 'general'),
                    token_count=chunk.get('token_count', 0)
                )
                session.add(report_chunk)
                session.flush()  # assign id for report_chunk

                chunk_ids.append(report_chunk.id)
                docs.append(chunk['text'])
                metas.append({
                    'report_id': report.id,
                    'repo_url': report.repo_url,
                    'section': chunk.get('section', 'general'),
                    'features_count': report.features_count,
                    'rules_count': report.rules_count,
                    'chunk_index': i
                })

            session.commit()

            # Upsert embeddings into Chroma (if available)
            try:
                client = get_client()
                if client:
                    upsert(ids=chunk_ids, embeddings=embeddings, metadatas=metas, documents=docs)
                else:
                    logger.warning('Chroma client not available; embeddings not persisted')
            except Exception as e:
                logger.error(f"Failed to upsert to Chroma: {e}")

            logger.info(f"✅ Processed report {report.id} with {len(chunks)} chunks")
            return report.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error processing report: {e}")
            raise
        finally:
            session.close()
