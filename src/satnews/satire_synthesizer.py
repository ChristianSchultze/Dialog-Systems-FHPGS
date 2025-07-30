import argparse
import json
import lzma
from pathlib import Path

from tqdm import tqdm

from src.satnews.model import make_llm
from src.satnews.utils import get_parser, module_wrapper

instructions = """
You are professional synthesis agent specializing in extracting key information from humorous or fictional news content.
You will receive a single raw satirical news article in json format and extract key information space efficiently.

Each article contains:
- Article Title
- Publication date
- Article Content

You need to prepare information that are important for matching the satirical news to an actual event.

Extract key jokes, satirical points, or notable fictional events.

Summarize the main idea of the satirical news. What or who is being mocked?

Extract information about key individuals, institutions, ideologies, companies or social behaviors.

BE CONCISE AND EFFICIENT USING BULLET POINTS
Don't tell anything about the output.
DONT RETURN ANYTHING ELSE.
Article:


"""
 
def synthesize_satire_with_ollama(satire_articles, llm, model = "llama3"):
    """Generate satirical commentary using Ollama LLM from extracted article data"""

    for key, article in tqdm(satire_articles.items(), desc="Synthesizing"):
            article["match_informations"] = llm(instructions, json.dumps(article), model)

    return satire_articles

def main(extracted_articles, args):
    llm = make_llm()

    invalid_json_keys = []
    for key, article in extracted_articles.items():
        if not isinstance(article, dict):
            invalid_json_keys.append(key)
    for key in invalid_json_keys:
        del extracted_articles[key]
    satire_output = synthesize_satire_with_ollama(extracted_articles, llm, "llama3")

    return satire_output


if __name__ == "__main__":
    description = "Synthesize satirical information as preparation for matching."
    output_file_name = "_satire_output.lzma"
    input_file_name = "_extracted.lzma"
    run_module = main

    parser = get_parser(description)
    module_wrapper(parser.parse_args(), output_file_name, input_file_name, run_module)
