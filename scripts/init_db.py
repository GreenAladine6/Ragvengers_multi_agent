#!/usr/bin/env python3
"""
Database initialization script for Gemini RAG Chatbot
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import db_manager
from database.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database"""
    load_dotenv()
    
    print("\n" + "="*60)
    print("🗄️  DATABASE INITIALIZATION")
    print("="*60)
    
    try:
        # Create engine and tables
        db_manager.init_db()
        
        print("\n✅ Database initialization completed successfully!")
        print("\n📊 Database URL:", os.getenv('DATABASE_URL', 'postgresql://localhost:5432/chatbot_db'))
        print("📁 Tables created:")
        print("   • reports - Stores business reports")
        print("   • report_chunks - Stores embeddings and chunks")
        print("   • conversations - Stores chat history")
        print("   • report_summaries - Stores summaries")
        
        print("\n🎯 Next steps:")
        print("   1. Make sure PostgreSQL has pgvector extension:")
        print("      CREATE EXTENSION IF NOT EXISTS vector;")
        print("   2. Upload reports:")
        print("      python load_reports.py")
        print("   3. Start the chatbot:")
        print("      python main.py")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        print(f"\n❌ Error: {e}")
        
        if "GEMINI_API_KEY" in str(e):
            print("\n📝 Please set GEMINI_API_KEY in .env file")
        elif "DATABASE_URL" in str(e):
            print("\n📝 Please set DATABASE_URL in .env file")
        elif "pgvector" in str(e).lower():
            print("\n📝 Please install pgvector extension:")
            print("   psql -d your_database -c 'CREATE EXTENSION IF NOT EXISTS vector;'")
        
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
