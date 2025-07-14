import ollama
from duckduckgo_search import DDGS
from datetime import datetime


def search_news(topic):
    """Search for news articles using DuckDuckGo"""
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=3)
        if results:
            news_results = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['href']}\nSummary: {result['body']}"
                for result in results
            ])
            return news_results
        return ""


def synthesize_news_with_ollama(news_text, model='llama3'):
    """Use Ollama to synthesize news text"""
    prompt = f"""
You are a professional news summarization assistant.  
Your task is to carefully read multiple news articles and produce a clear, concise, and well-structured summary report.

Input:  
You will receive several news articles. Each article contains:
- Title
- URL
- Summary

Task:
1. Organize the articles in a clean, readable format.
2. Identify shared topics or themes (for example: politics, technology, sports) and group related articles together.
3. For each group of related articles, write a brief synthesized summary combining the key points from those articles.
4. If an article does not fit into any group, list it under an 'Other News' section.

Output Format:
For each article, display:
- Title
- URL
- Published date
- Content

In a JSOn format.
Avoid using asterisks or informal language.
Focus on clarity, neutrality, and readability.
Do not copy article texts verbatim. Rephrase and synthesize information logically.
Keep the output professional and reader-friendly.

---

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
