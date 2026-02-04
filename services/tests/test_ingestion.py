import pytest
from services.ingestion.fetch_news import remove_bad_domains, html_cleaning

def test_remove_bad_domains():
    assert remove_bad_domains('https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_f8caa16b-a837-41b9-99d0-13e45d90067c') is True
    assert remove_bad_domains('https://www.bbc.com/news/articles/cp80ljjd5rwo') is False
    assert remove_bad_domains('https://www.cbsnews.com/video/sen-mark-kelly-venezuela/') is True

def test_html_cleaning():
    unclean = '<ul><li>40 million on alert for Arctic blast</li><li>How long will brutal cold last?</li><li>Trump ties Greenland threats to Nobel Peace Prize snub</li><li>Latest in Minneapolis after 2 weeks o… [+4411 chars]'
    clean = '40 million on alert for Arctic blast How long will brutal cold last? Trump ties Greenland threats to Nobel Peace Prize snub Latest in Minneapolis after 2 weeks o… [+4411 chars]'
    assert html_cleaning(unclean) == clean
    