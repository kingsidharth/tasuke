from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, SmallInteger, Date, Float, ARRAY, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression

Base = declarative_base()

class RawNote(Base):
    __tablename__ = 'raw_notes'
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)  # "slack", "granola"
    source_note_id = Column(String, nullable=False, unique=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)
    author = Column(String)
    channel = Column(String)
    content_vector = Column(ARRAY(Float, dimensions=1), nullable=True)  # pgvector placeholder
    received_at = Column(DateTime, server_default=func.now())
    __table_args__ = (UniqueConstraint('content_hash', name='uq_raw_notes_content_hash'),)
    def validate(self):
        pass

class Thread(Base):
    __tablename__ = 'threads'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status = Column(String, nullable=False, default="planning")
    completed_at = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    agent = Column(String)
    summary = Column(Text)
    summary_embedding = Column(ARRAY(Float, dimensions=1), nullable=True)  # pgvector placeholder
    def validate(self):
        pass

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey('threads.id'), nullable=False)
    content = Column(Text, nullable=False)
    content_vector = Column(ARRAY(Float, dimensions=1), nullable=True)  # pgvector placeholder
    role = Column(String, nullable=False)
    model = Column(String)
    tokens_used = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    content_hash = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint('role', 'content_hash', name='uq_messages_role_content_hash'),)
    def validate(self):
        pass

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    assignee = Column(String)
    status = Column(String, nullable=False, default="pending")
    priority = Column(SmallInteger)
    project_id = Column(Integer, ForeignKey('projects.id'))
    due_date = Column(Date, nullable=True)
    created_by = Column(String, nullable=False)
    updated_by = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    description_hash = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint('description_hash', name='uq_tasks_description_hash'),)
    def validate(self):
        pass

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    def validate(self):
        pass 