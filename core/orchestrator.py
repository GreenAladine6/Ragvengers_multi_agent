from langgraph.graph import StateGraph, END
from typing import Dict, Any
import asyncio
import time
from datetime import datetime

from core.state import SystemState, ProcessingStage
from agents.code_agent import CodeUnderstandingAgent
from agents.report_agent import ReportGeneratorAgent
from github.github_fetcher import GitHubFetcher
from feedback.collector import FeedbackCollector
from utils.logger import logger
from core.config import config

class AgentOrchestrator:
    """
    Simplified LangGraph orchestrator with performance tracking
    """
    
    def __init__(self):
        self.fetcher = GitHubFetcher()
        self.code_agent = CodeUnderstandingAgent()
        self.report_agent = ReportGeneratorAgent()
        self.feedback = FeedbackCollector()
        
        # Build graph
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Build the workflow graph"""
        workflow = StateGraph(SystemState)
        
        # Add nodes
        workflow.add_node("fetch", self.fetch_code)
        workflow.add_node("analyze", self.analyze_code)
        workflow.add_node("generate_report", self.generate_report)
        workflow.add_node("collect_feedback", self.collect_feedback)
        
        # Set entry point
        workflow.set_entry_point("fetch")
        
        # Add edges
        workflow.add_edge("fetch", "analyze")
        workflow.add_edge("analyze", "generate_report")
        workflow.add_edge("generate_report", "collect_feedback")
        
        # Conditional edge for feedback loop
        workflow.add_conditional_edges(
            "collect_feedback",
            self.should_improve,
            {
                True: "analyze",  # Re-analyze with feedback
                False: END
            }
        )
        
        return workflow.compile()
    
    async def fetch_code(self, state: SystemState) -> SystemState:
        """Fetch code with smart sampling to demonstrate scalability"""
        logger.info(f"Fetching code from {state['repo_url']}")
        state['stage'] = ProcessingStage.FETCHING
        state['started_at'] = datetime.now()
        
        try:
            # Fetch with sampling (show scalability)
            files, total_files = await self.fetcher.fetch_with_sampling(
                state['repo_url'],
                max_files=config.MAX_FILES_TO_FETCH
            )
            
            state['files'] = files
            state['files_fetched'] = len(files)
            state['total_files_in_repo'] = total_files
            state['api_calls'] = self.fetcher.api_calls
            state['cache_hits'] = self.fetcher.cache_hits
            
            logger.info(f"Fetched {len(files)}/{total_files} files")
            
        except Exception as e:
            state['errors'].append(str(e))
            state['stage'] = ProcessingStage.FAILED
            
        return state
    
    async def analyze_code(self, state: SystemState) -> SystemState:
        """Analyze code with batching for performance"""
        logger.info("Analyzing code...")
        state['stage'] = ProcessingStage.ANALYZING
        
        try:
            # Process in batches for scalability
            business_context = await self.code_agent.analyze_batch(
                state['files'],
                batch_size=config.BATCH_SIZE
            )
            
            state['business_context'] = business_context
            state['confidence_score'] = business_context.get('confidence', 0.0)
            state['files_processed'] = len(state['files'])
            
        except Exception as e:
            state['errors'].append(str(e))
            state['stage'] = ProcessingStage.FAILED
            
        return state
    
    async def generate_report(self, state: SystemState) -> SystemState:
        """Generate client report"""
        logger.info("Generating report...")
        state['stage'] = ProcessingStage.REPORTING
        
        try:
            report = await self.report_agent.generate(
                state['business_context'],
                {
                    'repo_url': state['repo_url'],
                    'files_analyzed': state['files_fetched'],
                    'total_files': state['total_files_in_repo'],
                    'confidence': state['confidence_score']
                }
            )
            
            state['report'] = report
            
        except Exception as e:
            state['errors'].append(str(e))
            state['stage'] = ProcessingStage.FAILED
            
        return state
    
    async def collect_feedback(self, state: SystemState) -> SystemState:
        """Collect and process feedback"""
        logger.info("Collecting feedback...")
        
        try:
            # In hackathon, this would be from user input
            # Here we simulate feedback based on confidence
            feedback = self.feedback.generate_simulated_feedback(state)
            state['feedback'] = feedback
            
            # Store corrections if any
            if feedback.get('corrections'):
                state['corrections'].extend(feedback['corrections'])
            
        except Exception as e:
            state['errors'].append(str(e))
            
        # Calculate processing time
        state['completed_at'] = datetime.now()
        state['processing_time'] = (
            state['completed_at'] - state['started_at']
        ).total_seconds()
        
        state['stage'] = ProcessingStage.COMPLETED
        return state
    
    def should_improve(self, state: SystemState) -> bool:
        """Decide if we should re-analyze with feedback"""
        # Re-analyze if we have corrections and confidence is low
        return (len(state.get('corrections', [])) > 0 and 
                state.get('confidence_score', 1.0) < config.CONFIDENCE_THRESHOLD)
    
    async def run(self, repo_url: str) -> Dict[str, Any]:
        """Run the complete workflow"""
        initial_state: SystemState = {
            'job_id': f"job_{int(time.time())}",
            'repo_url': repo_url,
            'files': {},
            'files_fetched': 0,
            'total_files_in_repo': 0,
            'business_context': None,
            'confidence_score': 0.0,
            'report': None,
            'feedback': None,
            'corrections': [],
            'processing_time': 0.0,
            'files_processed': 0,
            'api_calls': 0,
            'cache_hits': 0,
            'stage': ProcessingStage.FETCHING,
            'errors': [],
            'started_at': datetime.now(),
            'completed_at': None
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state