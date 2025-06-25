import os
from datetime import date
from urllib.parse import urlparse
import pandas as pd
from tqdm import tqdm

from src.utils import print_data_to_txt_file
from src.retrieval import retrieve_with_bing, retrieve_with_google
from src.property_detection.property_detection import FactCheckDetector


SITES_TO_EXCLUDE = ["www.reddit.com/*",
                    "www.twitter.com/*",
                    "www.x.com/*",
                    "www.facebook.com/*",
                    "www.threads.net/*",
                    "www.instagram.com/*",
                    "www.youtube.com/*",
                    "www.tiktok.com/*",
                    "www.nytimes.com/*",
                    "www.reuters.com/*",
                    "www.verifythis.com/*",
                    "www.pinterest.com/*",
                    "www.sacramento.newsreview.com/*",
                    "www.ncbi.nlm.nih.gov/pmc/articles/*"
]

def exclude_site(link):
    return any([site.replace("*","").replace("www.","") in link for site in SITES_TO_EXCLUDE])

def get_search_result_entries(claim_id, claim, page_title_list, url_list):
    search_result = []
    rank = 0
    for url_ix, url_val in enumerate(url_list):
        if not exclude_site(url_val):
            entry = {"claim_id": claim_id,
                    "claim": claim,
                    "search_rank": rank,
                    "link": url_val,
                    "title": page_title_list[url_ix],
                    "retrieval_date": date.today()}
            search_result.append(entry)
            rank += 1
    return search_result

def get_search_results(source_claims_path, save_folder, num_search_results):
    data = pd.read_csv(source_claims_path).set_index("id")
    print(f"Loaded {len(data)} claims to fetch search results for from '{source_claims_path}'.")
    print(f"Source claim columns: {data.columns.tolist()}")
    print()
    
    print("Starting retrieval of search results from Google and Bing:")
    print("The following webpages will be excluded:")
    for s in SITES_TO_EXCLUDE:
        print(s)
    print()
    
    google_search_results = []
    bing_search_results = []
    for claim_id, claim in tqdm(data.claim.items(), total=len(data)):
        page_title_list, url_list = retrieve_with_google.search(claim, num_search_results)
        google_search_results.extend(get_search_result_entries(claim_id, claim, page_title_list, url_list))
    
        page_title_list, url_list = retrieve_with_bing.search(claim)
        # the number of Bing results may vary - make sure the upper limit is followed
        max_no_pages = min(len(page_title_list), num_search_results)
        page_title_list = page_title_list[:max_no_pages]
        url_list = url_list[:max_no_pages]
        bing_search_results.extend(get_search_result_entries(claim_id, claim, page_title_list, url_list))
        
    google_search_results = pd.DataFrame(google_search_results)
    bing_search_results = pd.DataFrame(bing_search_results)
    
    # save the search results
    google_search_results.to_csv(os.path.join(save_folder, "google_result.csv"))
    bing_search_results.to_csv(os.path.join(save_folder, "bing_result.csv"))
    
    # TODO: print value counts of the number of search results retrieved per claim
    print("Distribution of number of links for Google:")
    print(google_search_results.groupby(["claim_id"]).link.count().value_counts())
    print()
    print("Distribution of number of links for Bing:")
    print(bing_search_results.groupby(["claim_id"]).link.count().value_counts())
    print()
    
    # fuse search results
    search_results = pd.merge(left=google_search_results,
                              right=bing_search_results,
                              how='outer',
                              on=['claim_id', 'claim', 'link', 'title'],
                              suffixes=["_google", "_bing"])
    search_results = search_results.sort_values(["claim_id", "search_rank_google", "search_rank_bing"], ignore_index=True)
    # use -1 to indicate that the link was not found by the other search engine
    search_results = search_results.fillna({"search_rank_google": -1, "search_rank_bing": -1})
    print(f"{len(search_results)} search results collected using Bing and Google.")
    print()

    # Indicate which sites are fact checking sites
    print("Checking for fact-check sites:")
    fact_check_detector = FactCheckDetector()
    search_results["is_fact_check_site"] = search_results.link.apply(fact_check_detector.is_fact_check_site)
    print(f"{len(search_results[search_results.is_fact_check_site])} search results come from a fact-check site.")
    
    # Check if any fact-check sites have been missed
    url_sites_fact = search_results[~(search_results.is_fact_check_site)]\
        .link[search_results.link.apply(lambda val: "fact" in val)].unique()
    url_sites_fact = list(set([urlparse(url).netloc.replace("www.","") for url in url_sites_fact]))
    missed_fact_filepath = os.path.join(save_folder, "potentially_missed_fc_sites.csv")
    print_data_to_txt_file(url_sites_fact, missed_fact_filepath)
    print(f"Potential fact-check sites that haven't been detected have been saved to '{missed_fact_filepath}'")
    print()
    
    # TODO: check for duplicated values (shouldn't be any)
    print("Checking for duplicated values:")
    duplicated_values = search_results[search_results.duplicated()]
    if len(duplicated_values) > 0:
        print(f"Warning: {len(duplicated_values)} duplicated values found.")
        print("Duplicated values:")
        print(duplicated_values)
    else:
        print("No duplicated values found!")
    print()
    
    # Give IDs and save
    def get_id_from_rank(row):
        bing_id_code = f"_b{int(row.search_rank_bing)}" if row.search_rank_bing > -1 else "_bn"
        google_id_code = f"_g{int(row.search_rank_google)}" if row.search_rank_google > -1 else "_gn"
        
        return f"{row.claim_id}_ret{bing_id_code}{google_id_code}"

    search_results["id"] = search_results.apply(get_id_from_rank, axis=1)
    search_results = search_results.set_index("id")
    
    save_file = os.path.join(save_folder, "search_results.csv")
    search_results.to_csv(save_file)
    print(f"Done! A total of {len(search_results)} search results have been saved to '{save_file}'.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get search results script")
    parser.add_argument("--source_claims_path", type=str, required=True, help="Path to the claim samples CSV file")
    parser.add_argument("--save_folder", type=str, required=True, help="Folder to save the data to")
    parser.add_argument("--num_search_results", type=int, default=20, help="Number of search results to fetch from each search engine for each claim")
    
    args = parser.parse_args()
    assert args.num_search_results%10==0
    
    results_file = os.path.join(args.save_folder, "search_results.csv")
    if os.path.isfile(results_file):
        print(f"A results file already exists for this script. ('{results_file}')")
        print("Remove it if you want to rerun the script.")
    else:
        os.makedirs(args.save_folder, exist_ok=True)
        get_search_results(args.source_claims_path, args.save_folder, args.num_search_results)