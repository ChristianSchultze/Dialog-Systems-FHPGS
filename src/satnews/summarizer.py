import re

from src.satnews.matcher import assemble_matching_data


def summarize(llm, model, matched_articles):
    if not matched_articles:
        return 'Sorry, no satirical news articles found.'

    real_healines = ""
    # for i, (real_news, satirical_news) in enumerate(matched_articles):
    #     real_healines += real_news["article_title"] + "\n"
    instructions = (f"""You are a news agent well versed in real events and especaially satirical news articles. 
        You are summarizing satirical news articles. You should present the 
        satirical news.. You behave like a real news agent, only that you use satirical news and are allowed to 
        make cross references between several satirical news for the same topic or in the same timeframe. 

        Dont exaplain every joke, dont talk about your task.
        Only output the news agent summary.

        REAL NEWS INFORMATION:

        Sports, Basketball, Baseball, Football
        
        
        AFTERWARDS:
        After your initial summary you will ask the user if they would like to know more about the stories and if you should explain anything.
        You are a satirical news Expert, so you are able to explain the various exaggaerations, what the satire is aimed at,
        what is being mocked or criticized.
        
        You have a search tool to your disposal, which can be called by 'SearchDDG[query]' replace query with your search query.
        Do not use the search tool in your initial response. Only use the search tool when system role states, that it is available.
        When using the search tool output only the search tool query. When responding to the user do not use the search tool.
        This can help you answer the users questions.
    """)
    promt_text = "SATIRICAL NEWS CONTENT \n \n \n"
    for i, (real_news, satirical_news) in enumerate(matched_articles):
        if i > 10:
            break
        promt_text += assemble_matching_data(satirical_news[1])
        promt_text += f"Satirical information: {satirical_news[1].get('content', 'N/A')}\n \n \n"
    result = llm(instructions, promt_text, model=model)
    return re.sub(r"SearchDDG\[(.*?)\]", "", result) # no queries in initial resultf