"""
Intelligent text chunking strategies for reports
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReportChunker:
    """Splits reports into optimal chunks for RAG"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def chunk_by_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk by report sections (executive summary, features, business rules)
        """
        chunks = []
        
        # Define section patterns
        section_patterns = {
            'executive_summary': r'(📋|EXECUTIVE|Summary)(.*?)(?=\n\n(📊|KEY|✨|🧮|📁|⚡)|$)',
            'key_metrics': r'(📊|KEY METRICS|Metrics)(.*?)(?=\n\n(✨|🧮|📁|⚡)|$)',
            'new_features': r'(✨|NEW FEATURES|Features)(.*?)(?=\n\n(🧮|📁|⚡)|$)',
            'business_rules': r'(🧮|BUSINESS RULES|Rules)(.*?)(?=\n\n(📁|⚡)|$)',
            'files_analyzed': r'(📁|FILES ANALYZED|Files)(.*?)(?=\n\n⚡|$)',
            'performance': r'(⚡|PERFORMANCE|Performance)(.*?)(?=$)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                section_text = match.group(2).strip() if match.lastindex >= 2 else match.group(0).strip()
                if section_text and len(section_text) > 20:
                    # Further chunk if section is too large
                    if len(section_text) > self.chunk_size * 2:
                        sub_chunks = self.chunk_by_size(section_text)
                        for i, sub_chunk in enumerate(sub_chunks):
                            chunks.append({
                                'text': sub_chunk,
                                'section': section_name,
                                'sub_index': i,
                                'token_count': len(sub_chunk.split())
                            })
                    else:
                        chunks.append({
                            'text': section_text,
                            'section': section_name,
                            'token_count': len(section_text.split())
                        })
        
        return chunks
    
    def chunk_by_size(self, text: str) -> List[str]:
        """
        Chunk by character size with overlap
        """
        chunks = []
        text_len = len(text)
        
        if text_len <= self.chunk_size:
            return [text]
        
        for i in range(0, text_len, self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            
        return chunks
    
    def chunk_report(self, report_text: str) -> List[Dict[str, Any]]:
        """
        Main chunking method - tries section-based first
        """
        # Try section-based chunking first
        chunks = self.chunk_by_sections(report_text)
        
        # If no sections found, fall back to size-based chunking
        if not chunks:
            size_chunks = self.chunk_by_size(report_text)
            for i, chunk in enumerate(size_chunks):
                chunks.append({
                    'text': chunk,
                    'section': 'general',
                    'sub_index': i,
                    'token_count': len(chunk.split())
                })
        
        logger.info(f"Created {len(chunks)} chunks from report")
        return chunks
    
    def extract_metadata(self, report_text: str) -> Dict[str, Any]:
        """
        Extract metadata from report for better retrieval
        """
        metadata = {}
        
        # Extract repo URL
        repo_match = re.search(r'(?:Repository|repo):\s*(https?://[^\s]+)', report_text, re.IGNORECASE)
        if repo_match:
            metadata['repo_url'] = repo_match.group(1).strip()
        
        # Extract metrics
        features_match = re.search(r'(?:Features?|New Features):\s*(\d+)', report_text, re.IGNORECASE)
        if features_match:
            metadata['features_count'] = int(features_match.group(1))
        
        rules_match = re.search(r'(?:Business Rules?|Rules):\s*(\d+)', report_text, re.IGNORECASE)
        if rules_match:
            metadata['rules_count'] = int(rules_match.group(1))
        
        files_match = re.search(r'Files Analyzed:\s*(\d+)', report_text, re.IGNORECASE)
        if files_match:
            metadata['files_analyzed'] = int(files_match.group(1))
        
        return metadata
