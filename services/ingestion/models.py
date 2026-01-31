'''Schema'''

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, DateTime
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