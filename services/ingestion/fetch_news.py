import os
import json
from dotenv import load_dotenv
from newsapi import NewsApiClient
from services.ingestion.db import session_local
from services.ingestion.models import Article
import hashlib
from typing import List
from urllib.parse import urlparse

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if NEWS_API_KEY is None:
    raise RuntimeError("NEWS_API_KEY is missing")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

exclude = ['consent.yahoo.com']

def get_news_articles(keyword: List[str], pages: int = 5) -> List:
    all_articles = []
    for word in keyword:
        for i in range(1, pages + 1):
            all_headlines = newsapi.get_everything(q=word, page=i)
            all_articles.extend(all_headlines['articles'])
    return all_articles

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
        url = article.get('url')
        if title in seen:
            continue
        if remove_bad_domains(url):
            continue
        seen.add(title)
        cleaned.append(article)
    return cleaned

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

def add_articles_to_db(keyword: List[str], pages: int):
    '''
    Docstring for add_articles_to_db
    
    :param pages: Pages of articles to get, 100 results per page
    :type pages: int
    :param keyword: Keyword/s or phrases to search for in article title and body from NewsAPI
    :type keyword: List[str]
    '''
    articles = get_news_articles(keyword, pages)
    articles = remove_duplicate_articles(articles)
    for a in articles:
        save_article(a)
    # with open('every_headline.json', 'w', encoding='utf-8') as f:
    #     json.dump(articles, f, indent=2)#, ensure_ascii=False)
    print(f'Extracted and inserted {len(articles)} articles...')

def remove_bad_domains(url):
    parse_url = urlparse(url)
    if parse_url.netloc in exclude:
        return True
    else:
        return False
    # print(parse_url.scheme)  # output: https
    # print(parse_url.netloc)  # output: www.example.com
    # print(parse_url.path)    # output: /path/page.html

def test():
    assert remove_bad_domains('https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_beaff8d3-671b-42bd-b3cf-5e3fcd0e1020') == False


if __name__ == '__main__':
    # political_keywords = ['trump', 'democracy', 'parliament', 'government']
    # fetch_articles = add_articles_to_db(keyword=political_keywords, pages=5)
    test()