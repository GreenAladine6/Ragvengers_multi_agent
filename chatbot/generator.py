"""
Response generation using Gemini with RAG context
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class GeminiGenerator:
    """Generates responses using Gemini with RAG context"""
    
    def __init__(self, api_key: str = None, system_prompt: str = None):
        if not genai:
            raise ImportError("Please install: pip install google-generativeai")
        
        import os
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.system_prompt = system_prompt or ""
        logger.info("✅ Gemini Generator initialized")
        
    def build_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Build prompt with RAG context
        """
        if not context_chunks:
            context_text = "No relevant documents found in the database."
            metadata_summary = ""
        else:
            # Format context
            context_text = ""
            for i, c in enumerate(context_chunks, 1):
                sim_pct = int(c['similarity'] * 100)
                context_text += f"\n[Document {i} - Relevance: {sim_pct}%]\n{c['text'][:500]}\n"
            
            # Extract metadata summary
            repos = set(c.get('repo_url') for c in context_chunks if c.get('repo_url'))
            avg_features = sum(c.get('features_count', 0) for c in context_chunks) / len(context_chunks) if context_chunks else 0
            avg_rules = sum(c.get('rules_count', 0) for c in context_chunks) / len(context_chunks) if context_chunks else 0
            
            metadata_summary = f"""
📊 Context Summary:
- Documents analyzed: {len(context_chunks)} chunks from {len(repos)} repositories
- Average features per report: {avg_features:.1f}
- Average business rules: {avg_rules:.1f}
"""
        
        prompt = f"""You are a helpful business analyst assistant that answers questions about software development reports. 
You have access to relevant sections from business impact analysis reports.

CONTEXT:
{context_text}

{metadata_summary}

Current date: {datetime.now().strftime('%Y-%m-%d')}

USER QUESTION: {query}

INSTRUCTIONS:
1. Answer based ONLY on the provided context
2. If the context doesn't contain the answer, say "I don't have information about that in the available reports"
3. Be specific about what you found
4. Use business-friendly language
5. Include relevant metrics when available
6. Cite which report sections you're referencing

Please provide a helpful and accurate answer:"""
        
        return prompt
    
    async def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate response using Gemini
        """
        try:
            logger.info(f"Generating response for: {query[:50]}...")
            
            # Build prompt with context
            prompt = self.build_prompt(query, context_chunks)
            if self.system_prompt:
                prompt = self.system_prompt + "\n\n" + prompt
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract citations
            citations = [
                {
                    'text': chunk['text'][:300] + '...',
                    'similarity': chunk['similarity'],
                    'section': chunk.get('section', 'unknown'),
                    'repo': chunk.get('repo_url', 'unknown')
                }
                for chunk in context_chunks[:3]  # Top 3 citations
            ]
            
            max_confidence = max(c['similarity'] for c in context_chunks) if context_chunks else 0
            
            logger.info(f"Generated response with confidence: {max_confidence:.2f}")
            
            return {
                'answer': response.text,
                'citations': citations,
                'chunks_used': len(context_chunks),
                'confidence': max_confidence
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'answer': f"I encountered an error generating a response: {str(e)}",
                'citations': [],
                'chunks_used': 0,
                'confidence': 0,
                'error': str(e)
            }
