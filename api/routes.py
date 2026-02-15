"""
FastAPI routes for the Gemini RAG Chatbot
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from chatbot.rag_pipeline import RAGPipeline
from database.connection import db_manager
from database.models import Report, Conversation, ReportChunk
from processor.embedder import GeminiEmbedder

logger = logging.getLogger(__name__)

app = FastAPI(
    title="🤖 Gemini RAG Chatbot",
    description="Answer questions about your business reports using AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global rag_pipeline
    
    logger.info("🚀 Starting Gemini RAG Chatbot...")
    
    # Check for API key (not required in mock mode)
    gemini_key = os.getenv('GEMINI_API_KEY')
    use_mock = os.getenv('USE_MOCK', '0') == '1'
    if not gemini_key and not use_mock:
        logger.error("❌ GEMINI_API_KEY not found in environment and not in mock mode")
        raise ValueError("GEMINI_API_KEY is required when not using mock services")
    
    # Initialize database
    try:
        db_manager.init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Initialize RAG pipeline
    try:
        rag_pipeline = RAGPipeline(gemini_key)
        logger.info("✅ RAG Pipeline initialized")
    except Exception as e:
        logger.error(f"RAG Pipeline initialization failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    db_manager.close()

# Request/Response models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 5

class ChatResponse(BaseModel):
    session_id: str
    query: str
    answer: str
    citations: List[dict]
    chunks_retrieved: int
    confidence: float
    timestamp: str

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int  # 1-5

class ReportUploadRequest(BaseModel):
    repo_url: str
    report_text: str
    metadata: Optional[dict] = None

# Routes
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    db_healthy = db_manager.health_check()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "rag_pipeline": "ready" if rag_pipeline else "initializing",
        "timestamp": str(datetime.utcnow().isoformat())
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - Ask questions about your reports
    
    Example:
    ```
    {
        "query": "What business rules were detected?",
        "top_k": 5
    }
    ```
    """
    if not rag_pipeline:
        logger.error("RAG Pipeline not initialized")
        raise HTTPException(status_code=503, detail="System initializing")
    
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if request.top_k and (request.top_k < 1 or request.top_k > 20):
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")
    
    try:
        response = await rag_pipeline.process_query(
            query=request.query,
            session_id=request.session_id,
            top_k=request.top_k or 5
        )
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/feedback")
async def add_feedback(request: FeedbackRequest) -> Dict[str, str]:
    """
    Add user feedback to a conversation
    
    Example:
    ```
    {
        "session_id": "abc123",
        "rating": 5
    }
    ```
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System initializing")
    
    if not 1 <= request.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    try:
        success = await rag_pipeline.add_feedback(request.session_id, request.rating)
        if success:
            return {"status": "success", "message": f"Feedback ({request.rating}/5) recorded"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error adding feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/upload")
async def upload_report(request: ReportUploadRequest) -> Dict[str, Any]:
    """
    Upload and process a new business report
    
    Example:
    ```
    {
        "repo_url": "https://github.com/user/repo",
        "report_text": "📊 Executive Summary...",
        "metadata": {"features_count": 5}
    }
    ```
    """
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="System initializing")
    
    if not request.report_text or len(request.report_text.strip()) < 100:
        raise HTTPException(status_code=400, detail="Report text too short (minimum 100 characters)")
    
    try:
        report_id = await rag_pipeline.embedder.process_report(
            report_text=request.report_text,
            repo_url=request.repo_url,
            metadata=request.metadata
        )
        logger.info(f"Report {report_id} uploaded successfully")
        return {
            "status": "success",
            "report_id": report_id,
            "message": "Report processed and indexed successfully"
        }
    except Exception as e:
        logger.error(f"Error uploading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get details about a specific report"""
    session = db_manager.get_session()
    try:
        report = session.query(Report).filter_by(id=report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "id": report.id,
            "repo_url": report.repo_url,
            "summary": report.summary,
            "features_count": report.features_count,
            "rules_count": report.rules_count,
            "files_analyzed": report.files_analyzed,
            "created_at": report.created_at.isoformat(),
            "chunks_count": len(report.chunks)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/reports")
async def list_reports(limit: int = 10) -> Dict[str, Any]:
    """List all uploaded reports"""
    session = db_manager.get_session()
    try:
        reports = session.query(Report)\
            .order_by(Report.created_at.desc())\
            .limit(limit)\
            .all()
        
        return {
            "total": len(reports),
            "reports": [
                {
                    "id": r.id,
                    "repo_url": r.repo_url,
                    "features_count": r.features_count,
                    "rules_count": r.rules_count,
                    "created_at": r.created_at.isoformat()
                }
                for r in reports
            ]
        }
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.get("/conversations/{session_id}")
async def get_conversation_history(session_id: str) -> Dict[str, Any]:
    """Get conversation history for a session"""
    try:
        history = await rag_pipeline.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "messages": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get system statistics"""
    session = db_manager.get_session()
    try:
        total_reports = session.query(Report).count()
        total_chunks = session.query(ReportChunk).count()
        total_conversations = session.query(Conversation).count()
        avg_feedback = session.query(func.avg(Conversation.feedback_score)).scalar()
        
        return {
            "total_reports": total_reports,
            "total_chunks": total_chunks,
            "total_conversations": total_conversations,
            "avg_feedback_rating": round(avg_feedback, 2) if avg_feedback else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return {"error": str(e)}
    finally:
        session.close()

from sqlalchemy import func

# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API info"""
    return {
        "name": "Gemini RAG Chatbot",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
