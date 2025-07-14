import lzma
import json
from itertools import islice

from satire_retriever import extract_articles_from_data, make_llm
from satire_synthesizer import synthesize_satire_with_ollama
from src.satnews.matcher import get_matched_articles
from src.satnews.summarizer import summarize


def main():
    # Load data
    with lzma.open("onion_data.lzma", "rb") as file:
        data = json.loads(file.read().decode("utf-8"))

    # Pick just one URL and its content
    one_url_data = list(islice(data.items(), len(data)))

    # Initialize local LLM
    llm = make_llm()

    # print("\n📄 Extracting article from URL...\n")
    # extracted_articles = extract_articles_from_data(one_url_data, llm)
    #
    # if not extracted_articles:
    #     print("❌ No articles extracted.")
    #     return
    #
    # # Print extracted JSON for inspection
    # # print("\n✅ Extracted Article:")
    # # print(json.dumps(extracted_articles, indent=2))
    # with lzma.open("extracted_articles.lzma", "wb") as file:
    #     file.write(json.dumps(extracted_articles).encode("utf-8"))

    # with lzma.open("extracted_articles.lzma", "rb") as file:
    #     extracted_articles = json.loads(file.read().decode("utf-8"))
    #
    # invalid_json_keys = []
    # for key, article in extracted_articles.items():
    #     if not isinstance(article, dict):
    #         invalid_json_keys.append(key)
    # for key in invalid_json_keys:
    #     del extracted_articles[key]
    # # Synthesize satire from the extracted article
    # print("\n🎭 Synthesizing satire...\n")
    # satire_output = synthesize_satire_with_ollama(extracted_articles, llm, "llama3")
    #
    # with lzma.open("satire_output.lzma", "wb") as file:
    #     file.write(json.dumps(satire_output).encode("utf-8"))

    with lzma.open("satire_output.lzma", "rb") as file:
        satire_output = json.loads(file.read().decode("utf-8"))

    # headlines = ""
    # for i, article in enumerate(list(reversed(satire_output.values()))):
    #     if i > 500:
    #         break
    #     for key in article.keys():
    #         if key and "title" in key.lower():
    #             headlines += f"{article[key]} \n"

    # instructions = """Identify and group article headlines by shared themes or topics.
    # Your task is to ONLY look at TECHNOLOGY AND SCIENCE headlines and subdivide them into further subcategories.
    # Use specific subcategories, they should not be too general.
    # Output only a list of subcategories and number of related articles.
    # """

    # instructions = """Identify and group article headlines by shared themes or topics.
    # Output only a list of categories and number of related articles.
    # """

    # instructions = "Give an overview of the sports related headlines in a structured format."
    # headlines += instructions
    #
    # print(llm(instructions, headlines, "llama3.3:70b"))

    real_data = """
- HST captures NGC 1786: A new image of a globular cluster
- Snow on SOAR Telescope: Unexpected frost in Chile may briefly impact observations Space.
- Fast X-ray transient linked to supernova: Gemini and SOAR capture this key insight into massive stars’ explosive deaths

- SPHEREx launched (Mar12, 2025): A near-IR all-sky spectrophotometer now mapping 450 million galaxies Wikipedia.
- China’s Tianwen‑2: Launched May28, heading to Kamoʻoalewa (2026 rendezvous) and main‑belt comet 311P/PANSTARRS
- Roman Space Telescope: NASA’s next-gen IR surveyor slated for launch in late 2026–early 2027
- India’s Venus Orbiter Mission (Shukrayaan) approved—aiming

- TESS finds new super‑Earth:
- JWST & HST deep dives: Recent revelations include:
  - JWST spotting Neptunian auroras, brown dwarfs, protostars, super-Jupiters, and galaxy evolution insights .

- July full moon (“Thunder Moon”)
- Meteor overlap next week: Southern Delta Aquariids and Alpha Capricornids
- July planetary lineup: Nights lit by Mars, Mercury mornings with Venus and Jupiter
- Citizen science catch: Kilonova Seekers app help led to discovery of a dwarf nova by amateur astronomer—first
#
# ### Policy & Funding
#
# - US NASA funding cuts: Proposed budget would slash Mars, Hubble, Webb"""
#
#     satire_slice = list(islice(satire_output.items(), len(data)))
#     matched_data = get_matched_articles(llm, model="gemma3:27b", satirical_data=satire_slice, real_data={"Recent space news": real_data})
#
#     print(json.dumps(matched_data))
#     with lzma.open("matched_data.lzma", "wb") as file:
#         file.write(json.dumps(matched_data).encode("utf-8"))

    with lzma.open("matched_data.lzma", "rb") as file:
        matched_data = json.loads(file.read().decode("utf-8"))

    output = summarize(llm, model="gemma3:27b", matched_articles=matched_data)

    print(json.dumps(output))
    with open("output.txt", "w") as file:
        file.write(output)

if __name__ == "__main__":
    main()
