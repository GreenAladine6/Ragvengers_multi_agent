"""
PostgreSQL database models with pgvector support for embeddings
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON, Integer, Float, ForeignKey, Date, Numeric, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

Base = declarative_base()

class Report(Base):
    """Stores the original business reports"""
    __tablename__ = 'reports'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url = Column(String(500), nullable=False, index=True)
    report_text = Column(Text, nullable=False)
    summary = Column(Text)
    features_count = Column(Integer, default=0)
    rules_count = Column(Integer, default=0)
    files_analyzed = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    report_metadata = Column(JSON, default={})
    
    # Relationship
    chunks = relationship('ReportChunk', back_populates='report', cascade='all, delete-orphan')
    summaries = relationship('ReportSummary', back_populates='report', cascade='all, delete-orphan')

class ReportChunk(Base):
    """Stores chunks of reports (embeddings stored in Chroma)"""
    __tablename__ = 'report_chunks'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer)
    token_count = Column(Integer, default=0)

    # NOTE: embeddings are stored in Chroma DB; do not store pgvector here
    # Metadata
    section = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    report = relationship('Report', back_populates='chunks')

class Conversation(Base):
    """Stores chat history and conversations"""
    __tablename__ = 'conversations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    retrieved_chunks = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    feedback_score = Column(Integer)
    
class ReportSummary(Base):
    """Stores pre-generated summaries for quick retrieval"""
    __tablename__ = 'report_summaries'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False)
    summary_type = Column(String(50))
    summary_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    report = relationship('Report', back_populates='summaries')
