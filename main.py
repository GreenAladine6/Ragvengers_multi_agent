# main.py
"""
Main entry point - Run the business report generator
"""

import asyncio
import argparse
from dotenv import load_dotenv

from core.orchestrator import BusinessReportOrchestrator
from core.config import config
from utils.logger import logger

# Load environment variables
load_dotenv()

# main.py - Update the print statements

async def main():
    parser = argparse.ArgumentParser(description='Generate business-friendly code reports')
    parser.add_argument('repo_url', help='GitHub repository URL')
    parser.add_argument('--files', nargs='+', 
                       default=['README.md', 'app/__init__.py', 'app/models.py', 
                               'app/templates/base.html', 'app/templates/index.html'],
                       help='Files to analyze')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("BUSINESS REPORT GENERATOR - Translating Code to Business Value")
    print("="*80)
    print(f"\nRepository: {args.repo_url}")
    print(f"Files to analyze: {len(args.files)}")
    
    # Validate config
    try:
        config.validate()
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        print("Please check your .env file")
        return
    
    # Run the orchestrator
    orchestrator = BusinessReportOrchestrator()
    await orchestrator.generate_report(args.repo_url, args.files)# main.py - Update the print statements

async def main():
    parser = argparse.ArgumentParser(description='Generate business-friendly code reports')
    parser.add_argument('repo_url', help='GitHub repository URL')
    parser.add_argument('--files', nargs='+', 
                       default=['README.md', 'app/__init__.py', 'app/models.py', 
                               'app/templates/base.html', 'app/templates/index.html'],
                       help='Files to analyze')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("BUSINESS REPORT GENERATOR - Translating Code to Business Value")
    print("="*80)
    print(f"\nRepository: {args.repo_url}")
    print(f"Files to analyze: {len(args.files)}")
    
    # Validate config
    try:
        config.validate()
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        print("Please check your .env file")
        return
    
    # Run the orchestrator
    orchestrator = BusinessReportOrchestrator()
    await orchestrator.generate_report(args.repo_url, args.files)

if __name__ == "__main__":
    asyncio.run(main())