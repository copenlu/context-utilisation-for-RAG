import os
import pandas as pd
from tqdm import tqdm

from src.retrieval.crawl_webpages import PageCrawler

def crawl_search_results(search_results_path, save_folder, crawled_pages_cache_path):
    search_results = pd.read_csv(search_results_path).set_index("id")
    print(f"Read {len(search_results)} search result samples from '{search_results_path}'.")
    print()
    
    # crawl pages
    print("Starting page crawling/lookup.")
    # crawler = PageCrawler(lookup_file=crawled_pages_cache_path)
    # for link in tqdm(search_results.link.unique()):
    #     crawler.crawl_page(link)
    crawler = PageCrawler(lookup_file=crawled_pages_cache_path, num_threads=7)
    crawler.crawl_pages(search_results.link.unique())
            
    search_results["content"] = search_results.link.apply(lambda val: crawler.webpage_content[val])
    search_results["url_date"] = search_results.link.apply(lambda val: crawler.webpage_date[val])
    print("Crawling done!")
    print()
    
    print("Error analysis:")
    failed_search_results_ix = search_results[(search_results.content.isna()) | (search_results.content=='') | (search_results.url_date.isna())].index
    print(f"Failed to fetch content for {len(failed_search_results_ix)} out of {len(search_results)} webpages.")
    failed_filepath = os.path.join(save_folder, "crawl_problem.csv")
    print(f"Storing failed examples to '{failed_filepath}'.")
    # Store the samples to allow for further analysis
    search_results.loc[failed_search_results_ix].to_csv(failed_filepath)

    print("Dropping the failed crawl samples.")
    search_results = search_results.drop(index=failed_search_results_ix)
    print()
    
    print("Crawled pages distribution:")
    print(search_results.groupby(["claim_id"]).link.count().value_counts())
    
    save_file = os.path.join(save_folder, "crawl_results.csv")
    search_results.to_csv(save_file)
    print(f"Done! A total of {len(search_results)} crawled search results have been saved to '{save_file}'.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawl search results script")
    parser.add_argument("--search_results_path", type=str, required=True, help="Path to the search results CSV file")
    parser.add_argument("--save_folder", type=str, required=True, help="Folder to save the data to")
    parser.add_argument("--crawled_pages_cache_path", type=str, required=True, help="Path to the crawled pages cache (will create a new one if it doesn't exist)")
    
    args = parser.parse_args()
    
    results_file = os.path.join(args.save_folder, "crawl_results.csv")
    if os.path.isfile(results_file):
        print(f"A results file already exists for this script. ('{results_file}')")
        print("Remove it if you want to rerun the script.")
    else:
        os.makedirs(args.save_folder, exist_ok=True)
        crawl_search_results(args.search_results_path, args.save_folder, args.crawled_pages_cache_path)