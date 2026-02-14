import sys
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import auth

# Add Astrafenix-AI to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Astrafenix-AI')))

try:
    from rag_pipeline import JiraRAGPipeline
except ImportError as e:
    # Fallback or mock if module not found (e.g. during initial setup)
    print(f"Warning: Could not import JiraRAGPipeline: {e}")
    print("Chatbot will use mock responses.")
    JiraRAGPipeline = None
except Exception as e:
    print(f"Error loading JiraRAGPipeline: {e}")
    JiraRAGPipeline = None

router = APIRouter(tags=["Chatbot"])

class ChatRequest(BaseModel):
    query: str
    project_key: str = "PRJ"

class ChatResponse(BaseModel):
    response: str

# Initialize pipeline globally or per request? 
# Usually globally is better for caching, but requires config.
# For now, we'll instantiate lazily or mock.
rag_pipeline = None

def get_rag_pipeline():
    global rag_pipeline
    if rag_pipeline is None and JiraRAGPipeline:
        # Load config from env
        domain = os.getenv("JIRA_DOMAIN", "your-domain.atlassian.net")
        email = os.getenv("JIRA_EMAIL", "your-email@example.com")
        token = os.getenv("JIRA_API_TOKEN", "your-token")
        rag_pipeline = JiraRAGPipeline(domain, email, token)
    return rag_pipeline

@router.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user = Depends(auth.get_current_active_user)):
    pipeline = get_rag_pipeline()
    if not pipeline:
        # Provide a mock intelligent response based on the query
        mock_response = f"Mock response to your query: '{request.query}' for project {request.project_key}. The RAG pipeline is not fully initialized yet. Please check your JIRA credentials in environment variables."
        return ChatResponse(response=mock_response)
    
    try:
        response = pipeline.query(request.query, request.project_key)
        return ChatResponse(response=response)
    except Exception as e:
        return ChatResponse(response=f"Error processing query: {str(e)}")
