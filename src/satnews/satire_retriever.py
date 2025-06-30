import requests
from bs4 import BeautifulSoup
import feedparser

def fetch_onion_articles(limit=5):
    """Fetch latest articles from The Onion"""
    url = 'https://www.theonion.com/rss'
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': BeautifulSoup(entry.summary, 'html.parser').get_text(),
            'image': extract_image_from_content(entry.summary)
        })
    return articles

def fetch_beaverton_articles(limit=5):
    """Fetch latest articles from The Beaverton front page"""
    url = 'https://www.thebeaverton.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []

    for article in soup.find_all('article')[:limit]:
        title_tag = article.find('h3', class_='entry-title')
        if title_tag and title_tag.a:
            title = title_tag.get_text(strip=True)
            link = title_tag.a['href']
            image_tag = article.find('img')
            image = image_tag['src'] if image_tag else None
            articles.append({
                'title': title,
                'link': link,
                'image': image
            })
    return articles

def fetch_postillon_articles(limit=5):
    """Fetch articles from The Postillon English version"""
    url = 'https://www.the-postillon.com/search/label/English'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []

    for article in soup.find_all('h3', class_='post-title entry-title')[:limit]:
        title_tag = article.find('a')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            articles.append({
                'title': title,
                'link': link
            })
    return articles

def extract_image_from_content(content_html):
    """Extract first image URL from HTML content"""
    soup = BeautifulSoup(content_html, 'html.parser')
    img_tag = soup.find('img')
    return img_tag['src'] if img_tag else None

def get_satirical_news():
    """Combine articles from all sources"""
    return {
        'The Onion': fetch_onion_articles(),
        'The Beaverton': fetch_beaverton_articles(),
        'The Postillon': fetch_postillon_articles()
    }

# Example run
if __name__ == "__main__":
    satire_news = get_satirical_news()
    for source, articles in satire_news.items():
        print(f"\n--- {source} ---")
        for article in articles:
            print(article)
