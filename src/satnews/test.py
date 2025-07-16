import csv
import lzma
import json
import lzma

import ollama

from satire_retriever import make_llm
from src.satnews.summarizer import summarize, make_llm_chat


def main():
    # Load data
    # with lzma.open("onion_data_2.lzma", "rb") as file:
    #     data = json.loads(file.read().decode("utf-8"))

    # with lzma.open("test_set_raw.lzma", "rb") as file:
    #     one_url_data = json.loads(file.read().decode("utf-8"))

    # Pick just one URL and its content
    # one_url_data = list(islice(data.items(), len(data)-100, len(data)))

    # with open('test_set.csv', 'w', newline='') as csvfile:
    #     spamwriter = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     for url, _ in one_url_data:
    #         spamwriter.writerow([url, 0])

    # ground_truth = []
    # with open('test_set.csv', newline='') as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    #     for row in spamreader:
    #         if bool(int(row[1])):
    #             ground_truth.append(row[0])
    #
    # # Initialize local LLM
    llm = make_llm()
    #
    # print("\n📄 Extracting article from URL...\n")
    # extracted_articles = extract_articles_from_data(one_url_data, llm)
    #
    # # with lzma.open("identified_articles_urls.lzma", "rb") as file:
    # #     extracted_articles = json.loads(file.read().decode("utf-8"))
    #
    # true_positive = 0
    # for url in extracted_articles.keys():
    #     if url in ground_truth:
    #         true_positive += 1
    # print(f"Precision: {true_positive/ len(extracted_articles)}")
    # print(f"Recall: {true_positive/ len(one_url_data)}")
    #
    # return


    # if not extracted_articles:
    #     print("❌ No articles extracted.")
    #     return

    # Print extracted JSON for inspection
    # print("\n✅ Extracted Article:")
    # print(json.dumps(extracted_articles, indent=2))

    with lzma.open("extracted_articles.lzma", "rb") as file:
        extracted_articles = json.loads(file.read().decode("utf-8"))

    with open('test_set.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for url in extracted_articles.keys():
            spamwriter.writerow([url, 0])

    return

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

    # with lzma.open("satire_output.lzma", "rb") as file:
    #     satire_output = json.loads(file.read().decode("utf-8"))

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

    real_data = """"""

    # satire_slice = list(islice(satire_output.items(), len(data)))
    # matched_data = get_matched_articles(llm, model="gemma3:27b", satirical_data=satire_slice, real_data={"Recent space news": real_data})
    #
    # print(json.dumps(matched_data))
    # with lzma.open("matched_data.lzma", "wb") as file:
    #     file.write(json.dumps(matched_data).encode("utf-8"))

    # with lzma.open("matched_data.lzma", "rb") as file:
    #     matched_data = json.loads(file.read().decode("utf-8"))
    #
    # chat = make_llm_chat()
    # model = "gemma3:27b"
    # output, messages = summarize(chat, model=model, matched_articles=matched_data)
    #
    # text = output
    # print(json.dumps(output))
    # with open("text_output.txt", "w") as file:
    #     file.write(text)
    # while True:
    #     user_input = input("You: \n")
    #     text += "You: \n"
    #     if user_input.strip().lower() == "exit":
    #         break
    #     messages.append({"role": "user", "content": user_input})
    #     text += user_input
    #     reply = ollama.chat(model=model, messages=messages, options={"num_ctx": 32768})['message']['content'].strip()
    #     print("Satirical News Agent: ", reply)
    #     text += "Satirical News Agent: "
    #     text += reply
    #     messages.append({"role": "assistant", "content": reply})
    #     with open("text_output.txt", "w") as file:
    #         file.write(text)

if __name__ == "__main__":
    main()
