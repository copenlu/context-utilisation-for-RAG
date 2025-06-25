import requests

from src.retrieval.retrieve_with_google import preprocess_query

with open("API-keys/bing-api-key.txt", "r") as f:
    BING_API_KEY = f.readline().strip()

class toSearch:
    def __init__(self, query):
        self.subscription_key = BING_API_KEY # key 1
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"
        self.query = query


def search(query):
    to_send = toSearch(preprocess_query(query))

    headers = {"Ocp-Apim-Subscription-Key": to_send.subscription_key}
    params = {"q": to_send.query, "textDecorations": True, "textFormat": "HTML", "count":50, "setlang":"en", "safeSearch":"Off"}
    # "responseFilter":"-images",
    #               "safeSearch":"Off", "setLang":"en"
    response = requests.get(to_send.search_url, headers=headers, params=params)
    response.raise_for_status()
    search_result = response.json()

    retrieved_pages = search_result["webPages"]["value"]

    page_list = [i["name"] for i in retrieved_pages]
    url_list = [i["url"] for i in retrieved_pages]

    return page_list, url_list
