import os
import json
from dotenv import load_dotenv
from newsapi import NewsApiClient
from services.ingestion.db import session_local
from services.ingestion.models import Article
import hashlib
from typing import List

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if NEWS_API_KEY is None:
    raise RuntimeError("NEWS_API_KEY is missing")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def remove_duplicate_articles(articles: List) -> List:
    '''
    Choosing to remove duplicate titles due to the pipeline is planned
    to only process titles, 
    Could do url but some urls differ with exact same article content
    Could also do title+author(+description), but unnecessary steps for now...  
    '''
    seen = set()
    cleaned = []
    for article in articles:
        title = article.get('title')
        if title in seen:
            continue
        seen.add(title)
        cleaned.append(article)
    return cleaned

def get_news_articles(pages: int) -> List:
    all_articles = []
    for i in range(1, pages + 1):
        all_headlines = newsapi.get_everything(q='trump', page=i)
        all_articles.extend(all_headlines['articles'])
    return all_articles

def make_id(source, title):
    return hashlib.sha256(f'{source}{title}'.encode()).hexdigest()

def save_article(article_data):
    db = session_local()
    try:
        article = Article(
            article_id = make_id(article_data['source']['name'], article_data['title']),
            source=article_data['source']['name'],
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

def add_articles_to_db(pages: int):
    articles = get_news_articles(pages)
    articles = remove_duplicate_articles(articles)
    for a in articles:
        save_article(a)
    with open('every_headline.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2)#, ensure_ascii=False)
    print(f'Extracted and inserted {len(articles)} articles...')


''' 
article_id = Column(String, primary_key=True)
source = Column(String, nullable=False)
title = Column(String, nullable=False)
description = Column(String, nullable=False)
content = Column(String)
published_at = Column(DateTime, default=datetime.now)
url = Column(String, nullable=False)
'''

if __name__ == '__main__':
    fetch_articles = add_articles_to_db(5)
    