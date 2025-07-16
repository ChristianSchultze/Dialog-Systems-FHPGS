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
from tqdm import tqdm


def make_llm():
    """Create an LLM callable that runs Ollama locally"""
    def llm(instructions: str, prompt: str, model: str = "llama3") -> str:
        response = ollama.chat(
            model=model,
            messages=[{"role": "system", "content": instructions}, {"role": "user", "content": prompt}],
            # options={"num_ctx": 8192}
            options={"num_ctx": 8192}
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
    
    identifier_instruction = """
    You are an HTML data analyzer.
    Your job is to decide from raw HTML code, whether the page is a content page containing article content.
    You need to figure out what is the main content of that HTML page, what is in CENTRAL VIEW when opeing the page?
    
    Output Format:
    Return a single float value ( 2 decimal places) between 0 and 1, representing your confidence that the page contains an article:
    1.0: Definitely article in central view
    0.0: Definitely no article central
    
    Dont explain your reasoning and only return the float value.
    """

    text_identifier_instruction = """
    Your task is to decide for the given text if it is coherent content of a news article.
    The content has to be related to itself and be at least five sentences long.
    
    You will receive json data, focus on the content element.
    
    Output Format:
    Return a single float value ( 2 decimal places) between 0 and 1, representing your confidence that the page contains an article:
    1.0: Definitely coherent content
    0.0: Definitely not coherent or very short
    
    Dont explain your reasoning and only return the float value.
    """

    extractor_instruction = """
    You are an HTML data extractor.
    Your job is to extract information about the main article on this page from raw HTML code and convert it into clean 
    JSON format.
    
    Focus on extracting:
    - Article title
    - Publication date
    - Article content
    - Image links clearly related to the main article
    
    Ignore:
    - Ads
    - Navigation
    - Unrelated text
    
    ONLY include RELATED text, NO Navigation, NO Ads, No unrelated text!
    OUTPUT ONLY RAW DATA IN JSON FORMAT
    
    Output Format:
    VALID JSON
    Keys:
    Headline
    Publication date
    Content
    Image links
    Don't tell anything about the JSON, Just return the JSON object.
    DONT RETURN ANYTHING ELSE.
    """

    extracted_articles = {}
    identified_articles_ids = []
    identified_articles_urls = []
    failed_json = 0
    failed_score = 0

    for index, (url, site) in tqdm(enumerate(data), desc="Identifying articles", total=len(data)):
        identified_articles_ids.append(index)
        identified_articles_urls.append(url)

    # for index, (url, site) in tqdm(enumerate(data), desc="Identifying articles", total=len(data)):
    #     if site == "Failed to retrieve." or site == "":
    #         continue
    #
    #     html_text = clean_html(site)
    #
    #     result = llm(identifier_instruction, html_text, "gemma3:12b")
    #
    #     try:
    #         result = result.strip().replace(",", "").replace("*","").replace("'", "")
    #         result_float = float(result)
    #         print("RESULT:", result)
    #     except ValueError:
    #         failed_score += 1
    #         print(f"\nSkipping {url}: invalid confidence score '{result}'\n")
    #         continue
    #
    #     if result_float >= 0.9:
    #         identified_articles_ids.append(index)
    #         identified_articles_urls.append(url)
    #
    # print(f"Number of failed float conversions: {failed_score}")
    # with lzma.open("identified_articles_urls.lzma", "wb") as file:
    #     file.write(json.dumps(identified_articles_urls).encode("utf-8"))

    for index in tqdm(identified_articles_ids, desc="Extracting articles"):
        extraction_result = llm(extractor_instruction, clean_html(data[index][1]))
        # print("\nRESULT:",extraction_result)
        try:
            article_json = json.loads(extraction_result)
            score = llm(text_identifier_instruction, extraction_result, "llama3")
        except json.JSONDecodeError:
            print(f"Skipping {data[index][0]}: invalid JSON extraction.")
            failed_json += 1
            continue

        try:
            score = score.strip().replace(",", "").replace("*","").replace("'", "")
            score = float(score)
            print("RESULT:", score)
        except ValueError:
            print(f"\nSkipping {url}: invalid confidence score '{score}'\n")
            continue

        if score >= 0.8:
            extracted_articles[data[index][0]] = article_json
    print(f"Number of failed json conversions: {failed_json}")
    with lzma.open("extracted_articles.lzma", "wb") as file:
        file.write(json.dumps(extracted_articles).encode("utf-8"))

    return extracted_articles
