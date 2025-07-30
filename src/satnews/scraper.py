import argparse
import json
import lzma
import time
from typing import Dict

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_same_domain(base_url, target_url):
    return urlparse(base_url).netloc == urlparse(target_url).netloc

def scrape_site(base_url: str) -> dict:
    result_data: Dict[str, str] = {}
    to_visit = {base_url}

    while to_visit:
        print(f"Yet to visit: {len(to_visit)}, Already visited: {len(result_data)}")
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
            response = requests.get(current_url, timeout=5)
            result_data[current_url] = response.text
            # print(f"Scraping: {current_url}")
        except requests.exceptions.Timeout:
            result_data[current_url] = "Failed to retrieve."
            print(f"Timeout {current_url}")
        except requests.RequestException as e:
            result_data[current_url] = "Failed to retrieve."
            print(f"Failed to fetch {current_url}: {e}")
            time.sleep(120)
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

def get_args():
    parser = argparse.ArgumentParser(description='Scrape website.')
    parser.add_argument(
        "--domain",
        "-d",
        type=str,
        required=True,
        help="The domain to scrape."
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    result = scrape_site(args.domain)
    with lzma.open("onion_data_save.lzma", "wb") as file:
        file.write(json.dumps(result).encode('utf-8'))


