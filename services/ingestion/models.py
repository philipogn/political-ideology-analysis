'''Schema'''

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    article_id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    content = Column(String)
    published_at = Column(DateTime, default=datetime.now)
    url = Column(String, nullable=False)

class InferenceResult(Base):
    __tablename__ = 'inference_result'
    id = Column(String, primary_key=True)
    article_id = Column(String, ForeignKey('articles.article_id', ondelete='CASCADE'), nullable=False)
    
    title = Column(String, nullable=False)
    published_at = Column(DateTime, default=datetime.now)
    axis_score = Column(Float)
    
