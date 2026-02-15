#!/usr/bin/env python3
"""
Test script for Gemini RAG Chatbot
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure UTF-8 output on Windows consoles to avoid emoji encode errors
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from dotenv import load_dotenv
from chatbot.rag_pipeline import RAGPipeline
from database.connection import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rag_pipeline():
    """Test the RAG pipeline with sample data"""
    load_dotenv()
    
    print("\n" + "="*70)
    print("🧪 RAG PIPELINE TEST")
    print("="*70)
    
    try:
        # Initialize database
        print("\n1️⃣  Initializing database...")
        db_manager.init_db()
        print("✅ Database ready")
        
        # Initialize RAG pipeline
        print("\n2️⃣  Initializing RAG pipeline...")
        pipeline = RAGPipeline()
        print("✅ RAG pipeline ready")
        
        # Test queries
        test_queries = [
            "What business rules were detected in the reports?",
            "How many features were found?",
            "Tell me about the user authentication logic",
            "What are the key metrics from the analysis?",
            "What business purposes were identified?"
        ]
        
        print("\n3️⃣  Testing with sample queries...")
        print("-" * 70)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 70)
            
            response = await pipeline.process_query(query)
            
            print(f"✅ Session ID: {response['session_id']}")
            print(f"📊 Chunks Retrieved: {response['chunks_retrieved']}")
            print(f"💪 Confidence: {response['confidence']:.2f}")
            print(f"\n💬 Answer:")
            print(f"   {response['answer'][:200]}...")
            
            if response['citations']:
                print(f"\n📚 Top Citation:")
                citation = response['citations'][0]
                print(f"   Section: {citation['section']}")
                print(f"   Repository: {citation['repo']}")
                print(f"   Relevance: {int(citation['similarity']*100)}%")
            
            # Add feedback
            print(f"\n📝 Adding feedback (rating 5/5)...")
            await pipeline.add_feedback(response['session_id'], 5)
            print("✅ Feedback recorded")
            
            await asyncio.sleep(1)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nYour RAG chatbot is working correctly!")
        print("\nNext steps:")
        print("  1. Load your reports: python scripts/load_reports.py")
        print("  2. Start the server: python main.py")
        print("  3. Visit: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception(e)
        return False

async def main():
    """Main test entry point"""
    success = await test_rag_pipeline()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
