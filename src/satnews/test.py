import lzma
import json
from satire_retriever import extract_articles_from_data, make_llm
from satire_synthesizer import synthesize_satire_with_ollama

def main():
    # Load data
    with lzma.open("onion_data.lzma", "rb") as file:
        data = json.loads(file.read().decode("utf-8"))

    # Pick just one URL and its content
    one_url_data = {}
    
    count = 0
    for url, content in data.items():
        if count >= 10:
            break# Limit to ten article
        one_url_data[url] = content
        count+=1

    # Initialize local LLM
    llm = make_llm()

    print("\n📄 Extracting article from URL...\n")
    extracted_articles = extract_articles_from_data(one_url_data, llm)

    if not extracted_articles:
        print("❌ No articles extracted.")
        return

    # Print extracted JSON for inspection
    print("\n✅ Extracted Article:")
    print(json.dumps(extracted_articles, indent=2))

    # Synthesize satire from the extracted article
    print("\n🎭 Synthesizing satire...\n")
    satire_output = synthesize_satire_with_ollama(extracted_articles)

    # Show result
    print("\n✅ Generated Satire:\n")
    print(satire_output)

if __name__ == "__main__":
    main()
