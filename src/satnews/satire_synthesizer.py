import ollama
from duckduckgo_search import DDGS

def search_news(topic, max_results=3):
    """Search for news articles using DuckDuckGo"""
    results_text = ""
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news", max_results=max_results)
        for result in results:
            results_text += f"Title: {result['title']}\nURL: {result['href']}\nSummary: {result['body']}\n\n"
    return results_text

def synthesize_news_with_ollama(news_text, model='llama3'):
    """Use Ollama to synthesize news text"""
    prompt = f"""

You are a professional news synthesis agent specializing in summarizing multiple articles into clear, factual, and well-structured reports.

Your responsibilities:

📥 Input:
You will receive a collection of raw news articles from different sources.

Each article contains:

Title:

Source Name:

URL (optional) :

Summary or Excerpt (optional) :

📊 📖 Task:
Organize the articles source-wise in a clean, structured format:

List each article under its respective source heading.

For each article, display:

Title

(optional) URL

(optional) Summary/Excerpt

Identify and group articles by shared themes or topics.
(e.g. if multiple articles talk about AI policy, or satirical celebrity coverage)

Extract key facts, events, and major points from the grouped content.

Combine information from multiple sources on the same topic into one comprehensive synthesis.

Structure your output as follows:

Articles:
{news_text}
"""
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

def process_news(topic):
    """Retrieve news and synthesize"""
    print(f"🔍 Searching for news about '{topic}'...")
    news_text = search_news(topic)

    if not news_text.strip():
        print("No news found.")
        return

    print("\n✅ News Retrieved. Synthesizing with Ollama...\n")
    summary = synthesize_news_with_ollama(news_text)
    print("📝 Synthesized Summary:\n")
    print(summary)

if __name__ == "__main__":
    topic = input("Enter a news topic: ")
    process_news(topic)
