"""
Main entry point for Gemini RAG Chatbot API Server
"""

import os
import sys
import logging
from pathlib import Path

# Add chatbot_ai to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        logger.error("❌ GEMINI_API_KEY not found in .env file")
        print("\nPlease configure .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Gemini API key from https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Check for database URL
    if not os.getenv('DATABASE_URL'):
        logger.warning("⚠️  DATABASE_URL not set, using default: postgresql://localhost:5432/chatbot_db")
        logger.warning("   Make sure PostgreSQL is running with pgvector extension")
    
    print("\n" + "="*70)
    print("🚀 Starting Gemini RAG Chatbot API Server")
    print("="*70)
    print("\n📚 System Configuration:")
    print("   • AI Engine: Google Gemini 1.5 Pro")
    print("   • Search: PostgreSQL + pgvector (Vector Database)")
    print("   • API Framework: FastAPI")
    print("\n🎯 Features:")
    print("   ✓ Semantic search across your reports")
    print("   ✓ AI-powered Q&A with citations")
    print("   ✓ Conversation memory and feedback")
    print("   ✓ Multi-report analysis")
    print("   ✓ Real-time streaming")
    print("\n🌐 API Server:")
    print("   • Host: http://0.0.0.0:8000")
    print("   • Documentation: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("\n💡 Quick Start:")
    print("   1. Load reports: python scripts/load_reports.py")
    print("   2. Ask a question: POST /chat with your query")
    print("   3. Rate answer: POST /feedback")
    print("\n" + "="*70 + "\n")
    
    # Start server
    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
