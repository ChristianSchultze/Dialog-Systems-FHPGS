import json
import lzma
from itertools import islice

import numpy as np
from tqdm import tqdm

from satnews.model import make_llm
from satnews.utils import module_wrapper, get_parser

def match_articles(llm, model, satirical_data, topic):
    matching_data = [0] * len(satirical_data)
    failed_score = 0
    instructions = (f"""You are a satirical news Expert and have to evaluate how well a real news topic matches to a single satirical news article.
    Match based on content similarity, thematic overlap, shared subjects, timing, or ideological commentary.
    Your input is in json format.

    TOPIC:
    {topic}
    
    OUTPUT FORMAT:
    Return a single float value between 0 and 1, representing your confidence that the topic matches the article:
    1.0: Clear match.
    0.0: Clearly not a match.
    Round to two decimal places max, e.g. 0.87, 0.42
    
    MATCH TO THE PROVIDED TOPIC
    Not related topics need to have a low score!
    Related topic need to have a high score!
    Dont explain your reasoning and only return the float value.
""")
    for j, (sat_url, satirical_article) in tqdm(enumerate(satirical_data), desc="Matching News",
                                                total=len(satirical_data)):
        result = llm(instructions, json.dumps(satirical_article), model)
        try:
            result = result.strip().replace(",", "").replace("*", "").replace("'", "")
            result = float(result)
            print(f"Matching Score {result}")
        except ValueError:
            failed_score += 1
            print(f"\nSkipping {sat_url}: invalid confidence score '{result}'\n")
            continue
        matching_data[j] = result
    print(f"Number of failed float conversions: {failed_score}")

    return np.array(matching_data)


def get_matched_articles(llm, model, satirical_data, topic):
    matching_data = match_articles(llm, model, satirical_data, topic)
    indices = np.array(np.where(matching_data > 0.9)[0]).T

    matched_articles = []
    for index in indices:
        json_data = satirical_data[index][1]
        json_data["original_url"] = satirical_data[index][0]
        matched_articles.append(json_data)

    return matched_articles


def main(data, args):
    llm = make_llm()
    satire_slice = list(islice(data.items(), len(data)))
    matched_data = get_matched_articles(llm, model="llama3", satirical_data=satire_slice, topic=args.topic)
    return matched_data


if __name__ == "__main__":
    description = "Matching News"

    input_file_name = "_satire_output.lzma"
    run_module = main

    parser = get_parser(description)
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Real topic description for matching with satirical news."
    )
    args = parser.parse_args()
    output_file_name = f"_matched_data[{args.topic}].lzma"
    module_wrapper(args, output_file_name, input_file_name, run_module)
