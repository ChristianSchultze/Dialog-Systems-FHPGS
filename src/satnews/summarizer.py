import json
import lzma
import re
from pathlib import Path

import ollama
from src.satnews.utils import get_parser, module_wrapper


def make_llm_chat():
    """Create an LLM callable that runs Ollama locally"""

    def llm_chat(instructions: str, prompt: str, model: str = "llama3") -> tuple:
        messages = [{"role": "system", "content": instructions}, {"role": "user", "content": prompt}]
        response = ollama.chat(
            model=model,
            messages=messages,
            # options={"num_ctx": 8192}
            options={"num_ctx": 32768}
        )
        return response['message']['content'].strip(), messages

    return llm_chat


def summarize(llm, model, matched_articles):
    if not matched_articles:
        return 'Sorry, no satirical news articles found.'

    instructions = (f"""You are a news agent well versed in real events and especaially satirical news articles. 
        You are summarizing satirical news articles and engaging in a conversation afterwards. You should present the 
        satirical news. You behave like a real news agent, only that you use satirical news and are allowed to 
        make cross references between several satirical news for the same topic or in the same timeframe. 

        Dont exaplain every joke, dont talk about your task.
        Only output the news agent summary.
        
        AFTERWARDS:
        DONT OUTPUT A SECOND SUMMARY
        RESPOND TO A QUESTION DIRECTLY
        
        After your initial summary you will ask the user if they would like to know more about the stories and if you should explain anything.
        You are a satirical news Expert, so you are able to explain the various exaggerations, what the satire is aimed at,
        what is being mocked or criticized.""")

    promt_text = "SATIRICAL NEWS CONTENT \n \n \n"
    for i, satirical_news in enumerate(matched_articles):
        if i > 10:
            break
        promt_text += json.dumps(satirical_news)
    result, messages = llm(instructions, promt_text, model=model)
    return result, messages


def main(matched_data):
    chat = make_llm_chat()
    model = "gemma3:27b"
    output, messages = summarize(chat, model=model, matched_articles=matched_data)

    text = output
    print(json.dumps(output))
    messages.append({"role": "system", "content": "Conversation starts, directly engage in conversation "
                                                  "and use previous messages as context."})
    while True:
        user_input = input("You: \n")
        text += "You: \n"
        if user_input.strip().lower() == "exit":
            break
        messages.append({"role": "user", "content": user_input})
        text += user_input
        reply = ollama.chat(model=model, messages=messages[1:], options={"num_ctx": 32768})['message']['content'].strip()
        print("Satirical News Agent: ", reply)
        text += "Satirical News Agent: "
        text += reply
        messages.append({"role": "assistant", "content": reply})
    return text


if __name__ == "__main__":
    description = "Summarize and chat satirical news agent."
    output_file_name = "chat.txt"
    input_file_name = "_matched_data.lzma"

    parser = get_parser(description)
    args = parser.parse_args()
    path = Path(args.path)
    stem = path.stem

    with lzma.open(path.parent / (stem + input_file_name), "rb") as file:
        input_data = json.loads(file.read().decode("utf-8"))
    limit = len(input_data) if args.limit is None else args.limit
    input_data = input_data[:limit]
    result = main(input_data)
    with lzma.open(path.parent / (stem + output_file_name), "wb") as file:
        file.write(json.dumps(result).encode("utf-8"))
