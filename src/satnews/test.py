from scraper import get_satirical_news
from satire_synthesizer import synthesize_news_with_ollama

def run_satirical_digest():
    print("🔍 Fetching satirical news articles...\n")
    satire_articles = get_satirical_news()

    # Convert articles to a text block for synthesis
    articles_text = ""
    for source, articles in satire_articles.items():
        articles_text += f"\n--- {source} ---\n"
        for article in articles:
            articles_text += f"Title: {article['title']}\nLink: {article['link']}\n"
            if 'summary' in article and article['summary']:
                articles_text += f"Summary: {article['summary']}\n"
            articles_text += "\n"

    if not articles_text.strip():
        print("No satirical articles found.")
        return

    print("✅ Satirical articles retrieved. Synthesizing digest with Ollama...\n")

    # Run Synthesizer
    summary = synthesize_news_with_ollama(articles_text)
    print("📝 Synthesized Satirical Digest:\n")
    print(summary)

if __name__ == "__main__":
    run_satirical_digest()
