"""
Dive AI Database Models
SQLAlchemy models for persistence
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from datetime import datetime
from database.config import Base


class ChatSession(Base):
    """Chat sessions table"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    channel = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class ChatMessage(Base):
    """Chat messages table"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    algorithm_used = Column(String, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    

class AlgorithmExecution(Base):
    """Algorithm execution logs"""
    __tablename__ = "algorithm_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    algorithm_name = Column(String, index=True, nullable=False)
    user_request = Column(Text, nullable=False)
    success = Column(Boolean, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    

class GeneratedAlgorithm(Base):
    """Track self-generated algorithms"""
    __tablename__ = "generated_algorithms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    algorithm_name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    source_code = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    success_rate = Column(Float, default=0.0)
    total_executions = Column(Integer, default=0)
