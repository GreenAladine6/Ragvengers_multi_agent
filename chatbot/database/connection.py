"""
PostgreSQL connection management with pgvector support
"""

import os
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL connection with pgvector"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/chatbot_db')
        self.engine = None
        self.Session = None
        
    def init_db(self):
        """Initialize database connection and create tables"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            
            # Enable pgvector extension
            with self.engine.begin() as conn:
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                except Exception as e:
                    logger.warning(f"Could not create pgvector extension: {e}")
                    logger.info("Please run: CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create session factory
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            
            # Import models and create tables
            from database.models import Base
            Base.metadata.create_all(self.engine)
            
            logger.info("✅ Database initialized with pgvector support")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            logger.error(f"Database URL: {self.database_url}")
            raise
        
    def get_session(self):
        """Get a database session"""
        if not self.Session:
            self.init_db()
        return self.Session()
    
    def close(self):
        """Close database connection"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
    
    def health_check(self):
        """Check database health"""
        try:
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Singleton instance
db_manager = DatabaseManager()
