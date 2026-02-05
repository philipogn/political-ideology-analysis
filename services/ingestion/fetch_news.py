import os
import json
from dotenv import load_dotenv
from newsapi import NewsApiClient
from services.ingestion.db import session_local
from services.ingestion.models import Article
import hashlib
from typing import List, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if NEWS_API_KEY is None:
    raise RuntimeError("NEWS_API_KEY is missing")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# cookie domain? doesn't contain any article info/content + third parties
exclude_domains = ['consent.yahoo.com', 'www.memeorandum.com'] 
bad_path_keywords = ['video', 'play', 'clip']

political_keywords = {
    'left-wing': [
        "wealth tax", "income inequality", "workers rights", "social welfare",
    ],

    'right-wing': [
        'deregulation', 'privatisation', "free market", "tax cuts", "deregulation", "small government",
    ],

    'authoritarian': [
        "national security", "border control", "surveillance laws",
    ],

    'libertarian': [
        "free speech", "privacy rights", "civil liberties",
    ]
}


def build_keyword_query(keywords: List[str]):
    return " OR ".join(f'"{word}"' for word in keywords)

def get_news_articles(keyword: Dict[str, List[str]], pages: int = 1) -> List:
    all_articles = []
    for word in keyword:
        for page in range(1, pages + 1): # each page holds 100 (defualt/maximum) articles
            all_headlines = newsapi.get_everything(
                q=word, 
                page=page, 
                language='en', 
            )
            for articles in all_headlines['articles']:
                articles['keyword'] = word
            all_articles.extend(all_headlines['articles'])
    return all_articles

def remove_bad_domains(url: str):
    '''
    Check for bad domains/video links
    '''
    if not url:
        return True
    
    parse_url = urlparse(url)
    if parse_url.netloc in exclude_domains:
        return True
    if any(keyword in parse_url.path.lower() for keyword in bad_path_keywords):
        return True
    return False

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
    # nevermind, md5 not collision resistant
    # uuid problems against possible duplicate entries

def html_cleaning(text):
    if not text:
        return text
    clean = BeautifulSoup(text, 'html.parser')
    return clean.get_text(separator=' ', strip=True)

def save_article(article_data):
    db = session_local()
    try:
        article = Article(
            article_id = make_id(article_data['source']['name'], article_data['title']),
            source=article_data['source']['name'],
            title=article_data['title'],
            description=html_cleaning(article_data['description']),
            content=html_cleaning(article_data['content']),
            keyword=article_data['keyword'],
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
    print(f'Extracted and inserted {len(articles)} articles...')

if __name__ == '__main__':
    political_keywords = ['trump', 'democracy', 'parliament', 'government', 'democrat', ] # should expand
    # fetch_articles = add_articles_to_db(keyword=political_keywords, pages=5)
    print(build_keyword_query(["wealth tax", "income inequality", "workers rights", "social welfare"]))