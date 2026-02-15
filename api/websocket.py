"""
Minimal WebSocket support for real-time chat (optional)
"""

import json
import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ChatWebSocketHandler:
    """Simple WebSocket handler for streaming responses"""
    
    def __init__(self, rag_pipeline):
        self.rag_pipeline = rag_pipeline
    
    async def handle(self, websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                payload = json.loads(data)
                query = payload.get('query')
                session_id = payload.get('session_id')
                if not query:
                    await websocket.send_text(json.dumps({'error': 'query missing'}))
                    continue
                # Process query (non-streaming example)
                result = await self.rag_pipeline.process_query(query, session_id=session_id)
                await websocket.send_text(json.dumps(result))
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await websocket.close()
