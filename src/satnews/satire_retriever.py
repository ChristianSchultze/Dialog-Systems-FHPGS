# import requests
# from bs4 import BeautifulSoup
# import feedparser

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

# def fetch_beaverton_articles(limit=5):
#     """Fetch latest articles from The Beaverton front page"""
#     url = 'https://www.thebeaverton.com/'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = []

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

# def fetch_postillon_articles(limit=5):
#     """Fetch articles from The Postillon English version"""
#     url = 'https://www.the-postillon.com/search/label/English'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     articles = []

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

# def extract_image_from_content(content_html):
#     """Extract first image URL from HTML content"""
#     soup = BeautifulSoup(content_html, 'html.parser')
#     img_tag = soup.find('img')
#     return img_tag['src'] if img_tag else None

# def get_satirical_news():
#     """Combine articles from all sources"""
#     return {
#         'The Onion': fetch_onion_articles(),
#         'The Beaverton': fetch_beaverton_articles(),
#         'The Postillon': fetch_postillon_articles()
#     }

# # Example run
# if __name__ == "__main__":
#     satire_news = get_satirical_news()
#     for source, articles in satire_news.items():
#         print(f"\n--- {source} ---")
#         for article in articles:
#             print(article)
import json
import lzma
from bs4 import BeautifulSoup
import re
import ollama


def make_llm():
    """Create an LLM callable that runs Ollama locally"""
    def llm(prompt: str) -> str:
        response = ollama.chat(
            model='llama3',
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()

    return llm


def clean_html(html: str) -> str:
    """Clean raw HTML by removing scripts, styles, and excessive whitespace"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for comment in soup.find_all(string=lambda s: isinstance(s, type(soup.Comment))):
        comment.extract()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_articles_from_data(data, llm):
    """Extract article info from data using LLM and return structured article dict"""
    
    article_instruction = """
You are an HTML data analyzer.
Your job is to decide from raw HTML code, whether the page is a content page containing an article.

Article Definition:
- A single main body of text
- A headline or title
- A timestamp or publication date
- Author attribution
- Paragraphs of text

Output Format:
Return a single float value ( 2 decimal places) between 0 and 1, representing your confidence that the page contains an article:
1.0: Definitely an article
0.0: Definitely not an article

Dont explain your reasoning and only return the float value.
"""

    extractor_instruction = """
You are an HTML data extractor.
Your job is to extract information about the main article on this page from raw HTML code and convert it into clean JSON format.

Focus on extracting:
- Article title
- Publication date
- Article content
- Image links clearly related to the main article

Output Format:
Don't tell anything about the JSON, Just return the JSON object.
DONT RETURN ANYTHING ELSE.
"""

    extracted_articles = {}
    
    for url, site in data.items():
        if site == "Failed to retrieve.":
            continue

        html_text = clean_html(site)

        article_prompt = article_instruction + "\n\n" + html_text
        result = llm(article_prompt)

        try:
            result = result.strip().replace(",", "").replace("*","").replace("'", "")
            print("RESULT:", result)
            result_float = float(result)
        except ValueError:
            print(f"Skipping {url}: invalid confidence score '{result}'")
            continue

        if result_float > 0.7:
            print("hello")
            extractor_prompt = extractor_instruction + "\n\n" + html_text
            extraction_result = llm(extractor_prompt)
            print("\nRESULT:",extraction_result)
            try:
                article_json = json.loads(extraction_result)
            except json.JSONDecodeError:
                print(f"Skipping {url}: invalid JSON extraction.")
                continue

            extracted_articles[url] = article_json
        


    return extracted_articles
