import os
import json
from dotenv import load_dotenv
from newsapi import NewsApiClient
from services.ingestion.db import session_local
from services.ingestion.models import Article
import hashlib

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if NEWS_API_KEY is None:
    raise RuntimeError("NEWS_API_KEY is missing")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

top_headlines = newsapi.get_top_headlines(sources='bbc-news',
                                          language='en')

# with open('top_headlines.json', 'w', encoding='utf-8') as f:
#     json.dump(top_headlines, f, indent=2, ensure_ascii=False)

# print(top_headlines)

def make_id(source, title):
    return hashlib.sha256(f'{source}{title}'.encode()).hexdigest()

def save_article(article_data):
    db = session_local()
    try:
        article = Article(
            article_id = make_id(article_data['source']['name'], article_data['title']),
            source=article_data['author'],
            title=article_data['title'],
            description=article_data['description'],
            content=article_data['content'],
            published_at=article_data['publishedAt'],
            url=article_data['url']
        )
        db.merge(article)
        db.commit()
    finally:
        db.close()

for a in top_headlines['articles']:
    save_article(a)

'''    article_id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    content = Column(String)
    published_at = Column(DateTime, default=datetime.now)
    url = Column(String, nullable=False)'''