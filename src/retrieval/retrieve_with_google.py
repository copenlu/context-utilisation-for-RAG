import time
import requests

MAX_NUM_PER_GOOGLE_SEARCH = 10

with open("API-keys/google-api-key.txt", "r") as f:
    API_KEY = f.readline().strip()
    
with open("API-keys/google-cx-with-fact-check.txt", "r") as f:
    CX_WITH_FC = f.readline().strip()

# preprocess the queries to make them compatible with the retrieval method
def preprocess_query(query):
    GOOGLE_SPECIFIC_CHARS = ['"', "AND", "OR", "|", "-", "*", "“", "”", "+"]
    for char in GOOGLE_SPECIFIC_CHARS:
        query = query.replace(char," ")
    return query

def claim_google_search(query, start="1", num="10"):
    # Documentation for the Google API can be found here: https://developers.google.com/custom-search/v1/overview.
    # - cx: A way to identify your custom google engine
    # - key: A way to identify your client to Google
    # - num: Number of search results to return
    # - start: The index of the first result to return
    # - q: Query context
    
    # exclude files from the search
    query = preprocess_query(query) + " -filetype:pdf -filetype:ppt -filetype:doc"
    params = {
        "cx":CX_WITH_FC,
        "key":API_KEY,
        "num":num,
        "start":start,
        "q":query,
    }
    url = "https://customsearch.googleapis.com/customsearch/v1"

    response = requests.get(url, params=params)
    if not response.ok:
        raise ValueError(f"Google API error: {response.json()}")
        
    if not search_results_found(response):
        print(f"No search results found for the query '{query}'.")
        print(response.json())
        if ("spelling" in response.json()) and ("correctedQuery" in response.json()["spelling"]):
            query = response.json()["spelling"]["correctedQuery"]
            print(f"Trying to search with the suggested corrected query '{query}' instead.")
            # we can at most make 100 requests to the Google API per minute
            time.sleep(0.6)
            
            params["q"] = query
            response = requests.get(url, params=params)
            if not response.ok:
                raise ValueError(f"Google API error: {response.json()}")
            if search_results_found(response):
                print("Corrected query worked!")
            else:
                print("Corrected query did not work. Skipping this sample.")
                return None
        else:
            return None
    
    # we can at most make 100 requests to the Google API per minute
    time.sleep(0.6)
    return response

def search_results_found(response):
    if response.json()["searchInformation"]["totalResults"] == "0":
        return False
    return True

def search(query, n):
    assert n%MAX_NUM_PER_GOOGLE_SEARCH==0, f"The number of search results to retrieve should be divisible by {MAX_NUM_PER_GOOGLE_SEARCH}"
    num_searches = int(n/MAX_NUM_PER_GOOGLE_SEARCH)
    start_ixs = [n*MAX_NUM_PER_GOOGLE_SEARCH+1 for n in range(num_searches)]
    title_list = []
    url_list = []
    for start_ix in start_ixs:
        response = claim_google_search(query, 
                                        start=f"{start_ix}", 
                                        num=f"{MAX_NUM_PER_GOOGLE_SEARCH}")
        if response is None:
            continue
        
        for val in response.json()["items"]:
            title_list.append(val["title"])
            url_list.append(val["link"])
        
    return title_list, url_list