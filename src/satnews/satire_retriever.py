import argparse
import json
import lzma
from itertools import islice
from pathlib import Path

from bs4 import BeautifulSoup
import re
from tqdm import tqdm

from satnews.model import make_llm
from satnews.utils import get_parser, module_wrapper


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


def extract_articles_from_data(data: dict, llm):
    """Extract article info from data using LLM and return structured article dict"""

    text_identifier_instruction = """
    Your task is to decide for the given text if it is coherent content of a news article.
    The content has to be related to itself and be at least five sentences long.
    
    You will receive json data.
    Output a low score for generic json content! 
    Following Keys (or similar) have to be present and filled with actual information!
    - Article title
    - Publication date
    - Article content
    
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
        - Article Title
        - Publication date
        - Article Content
        - Image links
        
    Don't tell anything about the JSON, Just return the JSON object.
    DONT RETURN ANYTHING ELSE.
    """

    extracted_articles = {}
    identified_articles_urls = []
    failed_json = 0
    failed_score = 0

    for url, site in data.items():
        identified_articles_urls.append(url)

    for url in tqdm(identified_articles_urls, desc="Identifying articles"):
        if data[url] == "Failed to retrieve.":
            continue
        extraction_result = llm(extractor_instruction, clean_html(data[url]))
        try:
            article_json = json.loads(extraction_result)
            score = llm(text_identifier_instruction, extraction_result, "llama3")
        except json.JSONDecodeError:
            print(f"Skipping {data[url]}: invalid JSON extraction.")
            failed_json += 1
            continue

        try:
            score = score.strip().replace(",", "").replace("*","").replace("'", "")
            score = float(score)
            print("RESULT:", score)
        except ValueError:
            print(f"\nSkipping {url}: invalid confidence score '{score}'\n")
            failed_score += 1
            continue

        if score >= 0.8:
            extracted_articles[url] = article_json
    print(f"Number of failed json conversions: {failed_json}")
    print(f"Number of failed float conversions: {failed_score}")

    return extracted_articles

def main(data, args):
    llm = make_llm()
    extracted_articles = extract_articles_from_data(data, llm)

    return extracted_articles

if __name__ == "__main__":
    description = "Scrape website."
    output_file_name = "_extracted.lzma"
    input_file_name = ".lzma"
    run_module = main

    parser = get_parser(description)
    module_wrapper(parser.parse_args(), output_file_name, input_file_name, run_module)