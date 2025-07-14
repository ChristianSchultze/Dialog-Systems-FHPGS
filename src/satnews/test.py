import lzma
import json
from itertools import islice

from satire_retriever import extract_articles_from_data, make_llm
from satire_synthesizer import synthesize_satire_with_ollama

def main():
    # Load data
    with lzma.open("onion_data.lzma", "rb") as file:
        data = json.loads(file.read().decode("utf-8"))

    # Pick just one URL and its content
    one_url_data = list(islice(data.items(), len(data)))

    # Initialize local LLM
    llm = make_llm()

    print("\n📄 Extracting article from URL...\n")
    extracted_articles = extract_articles_from_data(one_url_data, llm)

    if not extracted_articles:
        print("❌ No articles extracted.")
        return

    # Print extracted JSON for inspection
    # print("\n✅ Extracted Article:")
    # print(json.dumps(extracted_articles, indent=2))
    with lzma.open("extracted_articles.lzma", "wb") as file:
        file.write(json.dumps(extracted_articles).encode("utf-8"))

    # with lzma.open("extracted_articles.lzma", "rb") as file:
    #     extracted_articles = json.loads(file.read().decode("utf-8"))

    # Synthesize satire from the extracted article
    print("\n🎭 Synthesizing satire...\n")
    satire_output = synthesize_satire_with_ollama(extracted_articles, llm, "llama3")

    # Show result
    # print("\n✅ Generated Satire:\n")
    # print(satire_output)
    with lzma.open("satire_output.lzma", "wb") as file:
        file.write(json.dumps(satire_output).encode("utf-8"))

if __name__ == "__main__":
    main()
