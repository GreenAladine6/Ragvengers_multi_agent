#!/usr/bin/env python3
"""
Interactive CLI chatbot to test responses on screen
"""

import sys
import asyncio
import logging
from pathlib import Path

# Ensure UTF-8 output on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from chatbot.rag_pipeline import RAGPipeline
from database.connection import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Interactive chatbot CLI"""
    load_dotenv()
    
    print("\n" + "=" * 70)
    print("🤖 INTERACTIVE AI CHATBOT")
    print("=" * 70)
    print("\nInitializing...")
    
    try:
        # Initialize database
        db_manager.init_db()
        print("✅ Database ready")
        
        # Initialize RAG pipeline
        pipeline = RAGPipeline()
        print("✅ RAG Pipeline ready")
        
        print("\n" + "-" * 70)
        print("💬 Chat Interface (type 'exit' to quit)")
        print("-" * 70 + "\n")
        
        while True:
            # Get user input
            try:
                query = input("📝 You: ").strip()
            except EOFError:
                break
            
            if query.lower() in ('exit', 'quit', 'bye'):
                print("\n👋 Goodbye!")
                break
            
            if not query:
                continue
            
            try:
                # Process query
                print("\n🔄 Processing...\n")
                response = await pipeline.process_query(query, top_k=5)
                
                # Display response
                print("=" * 70)
                print(f"🤖 Chatbot Response:")
                print("=" * 70)
                print(f"\n{response['answer']}\n")
                
                # Display metadata
                print("-" * 70)
                print(f"📊 Confidence: {response.get('confidence', 0):.2%}")
                print(f"📚 Chunks Retrieved: {response.get('chunks_retrieved', 0)}")
                print(f"⏰ Session ID: {response.get('session_id', 'N/A')}")
                
                # Display citations if available
                citations = response.get('citations', [])
                if citations:
                    print(f"\n📖 Citations:")
                    for i, cite in enumerate(citations, 1):
                        print(f"   [{i}] {cite.get('section', 'unknown').upper()} "
                              f"({int(cite.get('similarity', 0) * 100)}% match)")
                        print(f"       Repo: {cite.get('repo', 'unknown')}")
                
                print("\n" + "=" * 70 + "\n")
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                logger.exception("Query processing error")
    
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        logger.exception("Initialization error")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
