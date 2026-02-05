'''Schema'''

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, UniqueConstraint, Index
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    article_id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)  
    description = Column(String, nullable=True)
    content = Column(String)
    keyword = Column(String, nullable=False)
    published_at = Column(DateTime, default=datetime.now)
    url = Column(String, nullable=False)

    inference_results = relationship('InferenceResult', back_populates='article')

class InferenceResult(Base):
    __tablename__ = 'inference_result'
    id = Column(String, primary_key=True)
    article_id = Column(String, ForeignKey('articles.article_id', ondelete='CASCADE'), nullable=False)

    model_version = Column(String, nullable=False) # to contain prompting techniques (zero shot, few shot...)
    
    econ_left = Column(Float, nullable=False)
    econ_right = Column(Float, nullable=False)
    social_auth = Column(Float, nullable=False)
    social_lib = Column(Float, nullable=False)

    x_coord = Column(Float, nullable=False) # right <-> left
    y_coord = Column(Float, nullable=False) # auth <-> lib

    title = Column(String, nullable=False)
    published_at = Column(DateTime, default=datetime.now)
    axis_score = Column(Float)

    article = relationship('Article', back_populates='inference_results')
    
    __table_args__ = (
        UniqueConstraint('article_id', 'model_version', name='unique_article_model_version'), # constrain to avoid dupes
        Index('ix_inference_article_id', 'article_id'),
        Index('ix_inference_model_version', 'model_version'),
        Index('ix_inference_xy', 'x_coord', 'y_coord')
    )