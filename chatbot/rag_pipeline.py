"""
Complete RAG pipeline orchestrator
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from database.connection import db_manager
from database.models import Conversation
import os

# Allow offline/mock mode for CI or local testing
USE_MOCK = os.getenv('USE_MOCK', os.getenv('USE_MOCK_GEN', '0')) == '1'
if USE_MOCK:
    from chatbot.mock_services import MockGeminiEmbedder as GeminiEmbedder
    from chatbot.mock_services import MockGeminiGenerator as GeminiGenerator
else:
    from processor.embedder import GeminiEmbedder
    from chatbot.generator import GeminiGenerator
from chatbot.retriever import VectorRetriever
from chatbot.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Orchestrates the complete RAG process"""
    
    def __init__(self, gemini_api_key: str = None):
        logger.info("Initializing RAG Pipeline...")
        self.embedder = GeminiEmbedder(gemini_api_key)
        self.retriever = VectorRetriever(self.embedder)
        self.generator = GeminiGenerator(gemini_api_key, system_prompt=SYSTEM_PROMPT)
        logger.info("✅ RAG Pipeline ready")
        
    async def process_query(
        self, 
        query: str, 
        session_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline
        """
        logger.info(f"Processing query: {query[:60]}...")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Step 1: Retrieve relevant chunks
        chunks = await self.retriever.retrieve(query, top_k=top_k)
        logger.info(f"Retrieved {len(chunks)} chunks")
        
        # Step 2: Generate response with context
        response = await self.generator.generate_response(query, chunks)
        logger.info(f"Generated response with confidence: {response.get('confidence', 0):.2f}")
        
        # Step 3: Store conversation in database
        session = db_manager.get_session()
        try:
            conversation = Conversation(
                session_id=session_id,
                user_message=query,
                bot_response=response['answer'],
                retrieved_chunks=[c['id'] for c in chunks] if chunks else [],
                created_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            logger.info(f"Stored conversation {session_id}")
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            session.rollback()
        finally:
            session.close()
        
        return {
            'session_id': session_id,
            'query': query,
            'answer': response['answer'],
            'citations': response.get('citations', []),
            'chunks_retrieved': len(chunks),
            'confidence': response.get('confidence', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def add_feedback(self, session_id: str, rating: int) -> bool:
        """
        Add user feedback to a conversation
        """
        if not 1 <= rating <= 5:
            logger.warning(f"Invalid rating: {rating}. Must be 1-5")
            return False
        
        session = db_manager.get_session()
        try:
            conversation = session.query(Conversation).filter_by(session_id=session_id).first()
            if conversation:
                conversation.feedback_score = rating
                session.commit()
                logger.info(f"Added feedback {rating}/5 to conversation {session_id}")
                return True
            else:
                logger.warning(f"Conversation {session_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    async def get_conversation_history(self, session_id: str) -> list:
        """
        Get conversation history for a session
        """
        session = db_manager.get_session()
        try:
            conversations = session.query(Conversation)\
                .filter_by(session_id=session_id)\
                .order_by(Conversation.created_at)\
                .all()
            
            history = [
                {
                    'user_message': c.user_message,
                    'bot_response': c.bot_response,
                    'created_at': c.created_at.isoformat(),
                    'feedback': c.feedback_score
                }
                for c in conversations
            ]
            return history
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
        finally:
            session.close()
