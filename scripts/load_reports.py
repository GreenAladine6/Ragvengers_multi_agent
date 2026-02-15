#!/usr/bin/env python3
"""
Script to load existing reports into the database
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from glob import glob

from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
from processor.chunker import ReportChunker

from database.connection import db_manager
from database.chroma_client import get_client, upsert

# Choose embedder implementation
USE_MOCK = os.getenv('USE_MOCK', '0') == '1'
if USE_MOCK:
    from chatbot.mock_services import MockGeminiEmbedder as GeminiEmbedder
else:
    from processor.embedder import GeminiEmbedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_reports_from_files(reports_dir: str):
    """
    Load all .txt report files from directory
    """
    # Initialize database
    db_manager.init_db()
    
    # Initialize embedder
    try:
        embedder = GeminiEmbedder(os.getenv('GEMINI_API_KEY'))
    except Exception as e:
        logger.error(f"Failed to initialize embedder: {e}")
        return False
    
    # Find all report files
    report_patterns = [
        os.path.join(reports_dir, "*.txt"),
        os.path.join(reports_dir, "*.md"),
        os.path.join(reports_dir, "**/*.txt"),
        os.path.join(reports_dir, "**/*.md")
    ]
    
    report_files = []
    for pattern in report_patterns:
        report_files.extend(glob(pattern, recursive=True))
    
    report_files = list(set(report_files))  # Remove duplicates
    
    if not report_files:
        logger.warning(f"No report files found in {reports_dir}")
        return False
    
    logger.info(f"Found {len(report_files)} report file(s)")
    
    # Load each report
    for i, report_file in enumerate(report_files, 1):
        try:
            logger.info(f"\n[{i}/{len(report_files)}] Processing {os.path.basename(report_file)}...")
            
            with open(report_file, 'r', encoding='utf-8') as f:
                report_text = f.read()
            
            if len(report_text.strip()) < 100:
                logger.warning(f"Report too short, skipping: {report_file}")
                continue
            
            # Extract repo URL from filename or content
            filename = os.path.basename(report_file)
            repo_url = f"file://{filename}"
            
            # Try to extract repo URL from content
            import re
            url_match = re.search(r'(https?://[^\s]+)', report_text)
            if url_match:
                repo_url = url_match.group(1)
            
            # Process report
            logger.info(f"Processing report from {repo_url}...")

            if USE_MOCK:
                # Manual processing for mock: create DB report, chunk, generate embeddings, upsert to Chroma
                session = db_manager.get_session()
                try:
                    report = None
                    from database.models import Report, ReportChunk

                    # create report record
                    report = Report(
                        repo_url=repo_url,
                        report_text=report_text,
                        features_count=0,
                        rules_count=0,
                        files_analyzed=[],
                        report_metadata={}
                    )
                    session.add(report)
                    session.flush()

                    chunker = ReportChunker()
                    chunks = chunker.chunk_report(report_text)

                    chunk_texts = [c['text'] for c in chunks]
                    embeddings = await embedder.generate_embeddings_batch(chunk_texts)

                    chunk_ids = []
                    docs = []
                    metas = []

                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        rc = ReportChunk(
                            report_id=report.id,
                            chunk_text=chunk['text'],
                            chunk_index=i,
                            section=chunk.get('section', 'general'),
                            token_count=chunk.get('token_count', 0)
                        )
                        session.add(rc)
                        session.flush()

                        chunk_ids.append(rc.id)
                        docs.append(chunk['text'])
                        metas.append({
                            'report_id': report.id,
                            'repo_url': repo_url,
                            'section': chunk.get('section', 'general'),
                            'features_count': 0,
                            'rules_count': 0,
                            'chunk_index': i
                        })

                    session.commit()

                    # Upsert embeddings into Chroma
                    try:
                        client = get_client()
                        if client:
                            upsert(ids=chunk_ids, embeddings=embeddings, metadatas=metas, documents=docs)
                            logger.info(f"✅ Loaded {filename} -> {report.id} (mock + Chroma upsert)")
                        else:
                            logger.warning('Chroma client not available; embeddings not persisted')
                    except Exception as e:
                        logger.error(f"Chroma upsert failed: {e}")

                except Exception as e:
                    session.rollback()
                    logger.error(f"Error processing (mock) {report_file}: {e}")
                finally:
                    session.close()

            else:
                report_id = await embedder.process_report(report_text, repo_url)
                logger.info(f"✅ Loaded {filename} -> {report_id}")
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error loading {report_file}: {e}")
            continue
    
    logger.info(f"\n✅ Successfully loaded all reports!")
    return True

async def main():
    load_dotenv()
    
    print("\n" + "="*60)
    print("📥 LOAD REPORTS INTO CHATBOT")
    print("="*60)
    
    # Get reports directory
    reports_dir = input("\nEnter path to reports directory (or press Enter for current dir): ").strip()
    if not reports_dir:
        reports_dir = "."
    
    if not os.path.isdir(reports_dir):
        print(f"❌ Directory not found: {reports_dir}")
        return False
    
    print(f"\n📂 Looking for reports in: {os.path.abspath(reports_dir)}")
    
    success = await load_reports_from_files(reports_dir)
    
    if success:
        print("\n🎉 All reports loaded successfully!")
        print("\nYou can now ask questions about your reports using the chatbot!")
    else:
        print("\n⚠️  No reports loaded. Please check the directory path.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
