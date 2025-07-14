import json
import lzma

with lzma.open("identified_articles_urls.lzma", "rb") as file:
    json_bytes = file.read()
    json_str = json_bytes.decode("utf-8")
json.loads(json_str)
print(json_str)
