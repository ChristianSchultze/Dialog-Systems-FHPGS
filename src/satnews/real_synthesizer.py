import ollama
from duckduckgo_search import DDGS
from datetime import datetime

MODEL = 'llama3'


def search_news(topic):
    """Search for news articles using DuckDuckGo, guided by structured agent-like instructions"""
    search_instructions = f"""
You are a dedicated news search specialist.

Responsibilities:
1. Search for the most recent, relevant, and credible news articles on the topic: "{topic}".
2. Prioritize results from reputable, reliable, and widely recognized news sources.
3. Avoid outdated, irrelevant, or unverified content.
4. Ensure results are diverse and cover different perspectives when possible.

Return:
- A structured list of results containing:
    - Title
    - URL
    - Summary (if available)

Exclude:
- Opinion pieces, satire, blogs unless explicitly about the topic.
- Prioritize official press releases and major news agency coverage.

Current date: {datetime.now().strftime('%Y-%m-%d')}
"""

    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=7)
        if results:
            news_results = "\n\n".join([
                f"Title: {result['title']}\nURL: {result['href']}\nSummary: {result['body']}"
                for result in results
            ])
            return news_results
        return ""


def synthesize_news_with_ollama(news_text, model=MODEL):
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
2. Identify shared topics or themes (e.g., politics, technology, sports) and group related articles together.
3. For each group of related articles, write a brief synthesized summary combining the key points from those articles.
4. If an article does not fit into any group, list it under an 'Other News' section.

Output Format:
Return the final result as a clean, valid JSON object containing:
- Groups (a list of thematic categories)
    - Each group should contain:
        - Group name
        - A brief summary of the group’s articles
        - A list of articles with:
            - Title
            - URL
            - Summary

Avoid using asterisks, markdown, or informal symbols.
Focus on clarity, neutrality, and readability.
Rephrase and synthesize information logically — do not copy verbatim.
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
    print(f"\n🔍 Searching for news about '{topic}'...\n")
    news_text = search_news(topic)

    if not news_text.strip():
        print("⚠️ No news found.")
        return

    print("\n✅ News Retrieved. Synthesizing with Ollama...\n")
    summary = synthesize_news_with_ollama(news_text)
    print("📝 Synthesized Summary:\n")
    print(summary)


if __name__ == "__main__":
    topic = input("Enter a news topic: ")
    process_news(topic)
