import json
import lzma
import time
from typing import Dict

import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse

from tqdm import tqdm


#
# def fetch_onion_articles(limit=5):
#     """Fetch latest articles from The Onion"""
#     url = 'https://www.theonion.com/rss'
#     feed = feedparser.parse(url)
#     articles = []
#     for entry in feed.entries[:limit]:
#         articles.append({
#             'title': entry.title,
#             'link': entry.link,
#             'published': entry.published,
#             'summary': BeautifulSoup(entry.summary, 'html.parser').get_text(),
#             'image': extract_image_from_content(entry.summary)
#         })
#     return articles
#
# def fetch_beaverton_articles(limit=5):
#     """Fetch latest articles from The Beaverton front page"""
#     url = 'https://www.thebeaverton.com/'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = []
#
#     for article in soup.find_all('article')[:limit]:
#         title_tag = article.find('h3', class_='entry-title')
#         if title_tag and title_tag.a:
#             title = title_tag.get_text(strip=True)
#             link = title_tag.a['href']
#             image_tag = article.find('img')
#             image = image_tag['src'] if image_tag else None
#             articles.append({
#                 'title': title,
#                 'link': link,
#                 'image': image
#             })
#     return articles
#
# def fetch_postillon_articles(limit=5):
#     """Fetch articles from The Postillon English version"""
#     url = 'https://www.the-postillon.com/search/label/English'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = []
#
#     for article in soup.find_all('h3', class_='post-title entry-title')[:limit]:
#         title_tag = article.find('a')
#         if title_tag:
#             title = title_tag.get_text(strip=True)
#             link = title_tag['href']
#             articles.append({
#                 'title': title,
#                 'link': link
#             })
#     return articles
#
# def extract_image_from_content(content_html):
#     """Extract first image URL from HTML content"""
#     soup = BeautifulSoup(content_html, 'html.parser')
#     img_tag = soup.find('img')
#     return img_tag['src'] if img_tag else None
#
# def get_satirical_news():
#     """Combine articles from all sources"""
#     return {
#         'The Onion': fetch_onion_articles(),
#         'The Beaverton': fetch_beaverton_articles(),
#         'The Postillon': fetch_postillon_articles()
#     }
#
# # Example run
# if __name__ == "__main__":
#     satire_news = get_satirical_news()
#     for source, articles in satire_news.items():
#         print(f"\n--- {source} ---")
#         for article in articles:
#             print(article)



def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def scrape_site(base_url: str) -> dict:

    with lzma.open("onion_data_2.lzma", "rb") as file:
        onion_data = json.loads(file.read().decode("utf-8"))

    for key in onion_data:
        onion_data[key] = ""

    with lzma.open("onion_to_visit_2.lzma", "rb") as file:
        onion_to_visit = json.loads(file.read().decode("utf-8"))

    result_data: Dict[str, str] = onion_data
    to_visit = set(onion_to_visit)

    while to_visit:
        print(len(to_visit))
        if len(result_data) %1000 == 0:
            print("SAVING")
            start = time.time()
            with lzma.open("onion_data_save.lzma", "wb") as file:
                file.write(json.dumps(result_data).encode('utf-8'))
            with lzma.open("onion_to_visit_save.lzma", "wb") as file:
                file.write(json.dumps(list(to_visit)).encode('utf-8'))
            print(f"DONE in {time.time() - start} seconds")

        current_url = to_visit.pop()
        if current_url in result_data:
            continue

        try:
            response = requests.get(current_url, timeout=10)
            result_data[current_url] = response.text
            # print(f"Scraping: {current_url}")
        except requests.exceptions.Timeout:
            result_data[current_url] = "Failed to retrieve."
            print(f"Timeout {current_url}")
        except requests.RequestException as e:
            result_data[current_url] = "Failed to retrieve."
            print(f"Failed to fetch {current_url}: {e}")
            continue

        extract_links(base_url, current_url, response.text, result_data, to_visit)

    return result_data


def extract_links(base_url, current_url, html, result_data, to_visit):
    start = time.time()
    soup = BeautifulSoup(html, 'html.parser')
    for link_tag in soup.find_all('a', href=True):
        if time.time() - start > 10:
            break
        href = link_tag['href']
        full_url = urljoin(current_url, href)

        # Only follow links within the same domain
        if is_same_domain(base_url, full_url) and full_url not in result_data:
            to_visit.add(full_url)


def fetch_onion_articles() -> dict:
    base_url = 'https://theonion.com/'
    return scrape_site(base_url)

html_data = fetch_onion_articles()


