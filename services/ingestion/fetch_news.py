import os
import json
from newsapi import NewsApiClient

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if NEWS_API_KEY is None:
    raise RuntimeError("NEWS_API_KEY is missing")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

top_headlines = newsapi.get_top_headlines(sources='bbc-news')

with open('top_headlines.json', 'w', encoding='utf-8') as f:
    json.dump(top_headlines, f, indent=2, ensure_ascii=False)

print(top_headlines)