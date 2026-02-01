import pytest
from services.ingestion.fetch_news import remove_bad_domains

def test_remove_bad_domains():
    assert remove_bad_domains('https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_f8caa16b-a837-41b9-99d0-13e45d90067c') is True
    assert remove_bad_domains('https://www.bbc.com/news/articles/cp80ljjd5rwo') is False