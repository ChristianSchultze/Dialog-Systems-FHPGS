import ollama

model_name = "llama3"

system_promt = ("""You are a satirical news Expert and have to evaluate how well a real news topic matches to a satirical news article.
                Output Format:
Return a single float value between 0 and 1, representing your confidence that the topic matches the article:
1.0: Clear match.
0.0: Very Unclear.
-1.0: Clearly not a match
Round to two decimal places max, e.g. 0.87, 0.42""")


