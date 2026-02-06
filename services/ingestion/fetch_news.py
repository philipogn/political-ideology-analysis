import os
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

class DataConfig():
    # cookie domain? doesn't contain any article info/content + third parties
    EXCLUDE_DOMAINS = ['consent.yahoo.com', 'www.memeorandum.com'] 
    BAD_PATH_KEYWORDS = ['video', 'play', 'clip']

    POLITICAL_KEYWORDS = {
        'left-wing': [
            "wealth tax", "income inequality", "workers rights", "social welfare",
        ],

        'right-wing': [
            "privatisation", "free market", "tax cuts", "deregulation", "small government",
        ],

        'authoritarian': [
            "national security", "border control", "surveillance laws",
        ],

        'libertarian': [
            "free speech", "privacy rights", "civil liberties",
        ]
    }

class FetchArticles(DataConfig):
    def __init__(self, ):
        # self.pages = pages
        pass

    def build_keyword_query(self, keywords: List[str]):
        return " OR ".join(f'"{word}"' for word in keywords)

    def get_news_articles(self, keyword: Dict[str, List[str]], pages: int = 1) -> List[Dict]:
        all_articles = []

        for axis, word in keyword.items():
            query = self.build_keyword_query(word)
            for page in range(1, pages + 1): # each page holds 100 (defualt/maximum) articles
                all_headlines = newsapi.get_everything(
                    q=query, 
                    page=page, 
                    language='en', 
                )
                for articles in all_headlines['articles']:
                    articles['matched_keyword_axis'] = axis
                all_articles.extend(all_headlines['articles'])
        return all_articles

    def is_bad_domain(self, url: str) -> bool:
        '''
        Check for bad domains/video links
        '''
        if not url:
            return True
        
        parse_url = urlparse(url)
        if parse_url.netloc in self.EXCLUDE_DOMAINS:
            return True
        if any(keyword in parse_url.path.lower() for keyword in self.BAD_PATH_KEYWORDS):
            return True
        return False

    def cleanup_articles(self, articles: List) -> List:
        '''
        Remove duplicate titles due to the pipeline is planned to only process titles, 
        Could do url but some urls differ with exact same article content
        Could also do title+author(+description), but unnecessary steps for now...  
        '''
        seen = set()
        cleaned = []
        for article in articles:
            title = article.get('title')
            description = article.get('description')
            content = article.get('content')
            url = article.get('url')
            if not title or not description or not content:
                continue
            if title in seen:
                continue
            if self.is_bad_domain(url):
                continue
            seen.add(title)
            cleaned.append(article)
        return cleaned

    def make_id(self, source, title):
        ''' Create primary key for article (MD5 not collision resistant, GUID possible duplicates)'''
        return hashlib.sha256(f'{source}{title}'.encode()).hexdigest()

    def html_cleaning(self, text):
        ''' Clean up html markup from fields in articles '''
        if not text:
            return text
        clean = BeautifulSoup(text, 'html.parser')
        return clean.get_text(separator=' ', strip=True)

    def save_article(self, article_data):
        ''' Add articles into the database '''
        db = session_local()
        try:
            article = Article(
                article_id = self.make_id(article_data['source']['name'], article_data['title']),
                source = article_data['source']['name'],
                title = article_data['title'],
                description = self.html_cleaning(article_data['description']),
                content = self.html_cleaning(article_data['content']),
                matched_keyword_axis = article_data['matched_keyword_axis'],
                published_at = article_data['publishedAt'],
                url = article_data['url']
            )
            db.merge(article)
            db.commit()
        finally:
            db.close()

    def add_articles_to_db(self, keyword: Dict[str, List[str]], pages: int):
        '''
        Docstring for add_articles_to_db
        
        :param pages: Pages of articles to get, 100 results per page
        :type pages: int
        :param keyword: Keyword/s or phrases to search for in article title and body from NewsAPI
        :type keyword: List[str]
        '''
        articles = self.get_news_articles(keyword, pages)
        cleaned_articles = self.cleanup_articles(articles)
        for a in cleaned_articles:
            self.save_article(a)
        print(f'Extracted and inserted {len(cleaned_articles)} articles...')

if __name__ == '__main__':
    fetch = FetchArticles()
    config = DataConfig()
    fetch.add_articles_to_db(keyword=config.POLITICAL_KEYWORDS, pages=5)