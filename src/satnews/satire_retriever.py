import json
import lzma
from typing import Callable

import torch
from smolagents import CodeAgent
from bs4 import BeautifulSoup
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


def make_llm() -> Callable:
    generator = pipeline("text-generation", model="huggyllama/llama-7b", torch_dtype=torch.float16, device=0)
    def llm(promt: str) -> str:
        result = generator(promt, max_neww_tokens=512, do_sample=True, temperature=0.7)[0]["generated_text"]
        return result[len(promt):].strip()

    return llm

def clean_html(html: str) -> str:
    """Clean raw HTML by removing javascript and css information and removing obsolete whitespaces to reduce
    token count for LLM processing."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    for comment in soup.find_all(string=lambda s: isinstance(s, type(soup.Comment))):
        comment.extract()

    text = soup.get_text(separator="\n")

    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

with lzma.open("onion_data.lzma", "rb") as file:
    json_bytes = file.read()
    json_str = json_bytes.decode("utf-8")
data = json.loads(json_str)

llm = make_llm()

article_instruction = """
You are an HTML data analyzer.
Your job is to decide from raw HTML code, whether the page is a content page containing an article. 

Article Definition:
A single main body of text,
A headline or title,
A timestamp or publication data,
Author attribution,
Paragraphs of text.

Output Format:
Return a single float value between 0 and 1, representing your confidence that the page contains an article:
1.0: Definitely an article
0.0: Definitely not an article
Round to two decimal places max, e.g. 0.87, 0.42
"""

extractor_instruction = """
You are an HTML data extractor.
Your job is to extract information about the main article on this page from raw HTML code and convert it into clean 
JSON format.

Focus on extracting:
- Article title
- Publication date. 
- Article content
- Image links that are clearly related to the main article.

Return only JSON.
"""
article_agent = CodeAgent(llm=llm)
article_agent.plan(article_instruction)

extractor_agent = CodeAgent(llm=llm)
extractor_agent.plan(extractor_instruction)

for url, site in data.items():
    if site == "Failed to retrieve.":
        continue
    result = article_agent.run(f"Decide this page: \n\n{clean_html(site)}")
    result = article_agent.run(f"Extract info from the following HTML: \n\n{clean_html(site)}")



