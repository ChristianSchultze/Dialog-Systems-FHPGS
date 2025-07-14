import numpy as np

def assemble_matching_data(data) -> str:
    articles_text = f"Title: {data.get('article_title', 'N/A')}\n"
    articles_text += f"Published: {data.get('publication_date', 'N/A')}\n"
    articles_text += f"Satirical information: {data.get('match_informations', 'N/A')}\n"
    return articles_text

def match_articles(llm, satirical_data, real_data):
    real_urls = []
    satirical_urls = []
    matching_data = [[0]*len(satirical_data)]*len(real_data)
    failed_score = 0
    for i, (url, article) in enumerate(real_data.values()):
        real_urls.append(url)
        instructions = (f"""You are a satirical news Expert and have to evaluate how well a real news article matches to a single satirical news article.
        You will be given information about a real news article, and then analyze information prepared for a satirical news article.
        Evaluate the given real news for relevance to the satirical content. Match based on event similarity, thematic overlap, shared subjects, timing, or ideological commentary.
                        
                        
                        REAL NEWS ARTICLE DATA: 
    
    {assemble_matching_data(article)}
                        
                        
                        OUTPUT FORMAT:
        Return a single float value between 0 and 1, representing your confidence that the topic matches the article:
        1.0: Clear match.
        0.0: Very Unclear.
        -1.0: Clearly not a match
        Round to two decimal places max, e.g. 0.87, 0.42
        Dont explain your reasoning and only return the float value.
    """)
        for j, (sat_url, satirical_article) in enumerate(satirical_data.values()):
            satirical_urls.append(sat_url)
            result = llm(instructions, assemble_matching_data(satirical_article))
            try:
                result = result.strip().replace(",", "").replace("*", "").replace("'", "")
                result = float(result)
                print(result)
            except ValueError:
                failed_score += 1
                print(f"\nSkipping {sat_url}: invalid confidence score '{result}'\n")
                continue
            matching_data[i][j] = result
    print(f"Number of failed float conversions: {failed_score}")

    return np.array(matching_data), real_urls, satirical_urls

def get_matched_articles(llm, satirical_data, real_data):
    matching_data, real_urls, satirical_urls = match_articles(llm, satirical_data, real_data)
    indices = np.where(matching_data > 0.6)

    matched_articles = []
    for index in indices:
        url_pair = (real_urls[index], matching_data[index])
        article_pair = (real_data[url_pair[0]], real_data[url_pair[1]])
        matched_articles.append(article_pair)

    return matched_articles


