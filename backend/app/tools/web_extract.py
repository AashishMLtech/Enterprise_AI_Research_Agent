"""Normalized web extraction boundary using Newspaper3k."""

from newspaper import Article


def extract_article(url: str) -> dict:
    article = Article(url)
    article.download()
    article.parse()
    return {
        "url": url,
        "title": article.title,
        "text": article.text,
        "published_at": article.publish_date,
        "authors": article.authors,
    }
