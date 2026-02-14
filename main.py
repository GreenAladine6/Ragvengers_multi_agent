#!/usr/bin/env python3
"""
Multi-Agent System - Hackathon Demo
"""

import asyncio
import argparse
import warnings
from datetime import datetime
import json

from core.orchestrator import AgentOrchestrator
from utils.logger import logger
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Silence known langchain/pydantic compatibility warning on Python 3.14
warnings.filterwarnings(
    "ignore",
    message=r"Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater\.",
)

# Access variables
API_KEY = os.getenv('API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  
MAX_FILES = int(os.getenv('MAX_FILES_TO_FETCH', '20'))

async def main():
    parser = argparse.ArgumentParser(description='Multi-Agent Code Analysis System')
    parser.add_argument('repo_url', nargs='?', help='GitHub repository URL')
    parser.add_argument('--max-files', type=int, default=20, 
                       help='Maximum files to fetch (default: 20)')
    parser.add_argument('--output', '-o', default='report.html',
                       help='Output file for report')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 Multi-Agent System - Hackathon Demo")
    print("="*60)
    print(f"\nRepository: {args.repo_url}")
    print(f"Max files: {args.max_files}")
    print(f"Output: {args.output}\n")
    
    # Determine repo URL (positional arg -> env -> fallback sample)
    repo_url = args.repo_url or os.getenv('REPO_URL') or 'https://github.com/octocat/Hello-World'

    # Override config
    from core.config import config
    config.MAX_FILES_TO_FETCH = args.max_files
    
    # Run system
    start_time = datetime.now()
    orchestrator = AgentOrchestrator()
    
    print("🔄 Running workflow...")
    result = await orchestrator.run(repo_url)
    
    # Print results
    print("\n" + "="*60)
    print("✅ Analysis Complete!")
    print("="*60)
    print(f"\n📊 Results:")
    print(f"  • Files fetched: {result['files_fetched']}/{result['total_files_in_repo']}")
    print(f"  • Confidence score: {result['confidence_score']*100:.1f}%")
    print(f"  • Processing time: {result['processing_time']:.2f}s")
    print(f"  • API calls: {result['api_calls']}")
    print(f"  • Cache hits: {result['cache_hits']}")
    
    # Save report
    if result['report']:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['report']['html'])
        print(f"\n📄 Report saved to: {args.output}")
        
        # Also save JSON
        json_output = args.output.replace('.html', '.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            f.write(result['report']['json'])
        print(f"📋 JSON data saved to: {json_output}")

    # Save fetched files separately for easy viewing (path + first 2KB)
    try:
        fetched = result.get('files', {})
        if fetched:
            out = {}
            for p, info in fetched.items():
                content = info.get('content', '')
                out[p] = {
                    'size': info.get('size', len(content)),
                    'snippet': content[:2048]
                }
            with open('fetched_files.json', 'w', encoding='utf-8') as ff:
                json.dump(out, ff, indent=2)
            print(f"🗂️ Fetched files saved to: fetched_files.json")
    except Exception:
        pass
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())