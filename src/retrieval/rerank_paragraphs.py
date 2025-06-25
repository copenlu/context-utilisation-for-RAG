import os
import time
import csv
from ast import literal_eval
import pandas as pd
from tqdm import tqdm
import cohere

RERANK_MAX_NBR_DOCUMENTS = 10000 # fixed by Cohere
RERANK_SCORE_THRESHOLD = 0.003 # tuned by Lovisa

with open("API-keys/cohere-api-key.txt", "r") as f_co:
    api_key = f_co.readline().strip()
co = cohere.Client(api_key=api_key)

def print_list_to_csv_file(l, filepath):
    with open(filepath, 'a') as f:
        w = csv.writer(f, delimiter=',', lineterminator='\n')
        w.writerow(l)
        
def read_lists_from_csv_file(filepath, as_int=False):
    with open(filepath, 'r') as f: 
        csv_reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC) 
        # convert string to list 
        l = list(csv_reader) 
    if as_int:
        l = [[int(val) for val in sub_list] for sub_list in l]
    return l

def init_from_cache_file(cache_file, as_int=False):
    if not os.path.exists(cache_file):
        # initialize the cache
        print(f"No cache file found. Setting up a new one at '{cache_file}'.")
        return []
    else:
        # load an existing url-content lookup
        print(f"A cache file was found at '{cache_file}'. Loading the entries..")
        return read_lists_from_csv_file(cache_file, as_int)

def read_pandas_file_with_lists(filepath, list_cols):
    def convert_string_to_list(val):
        try:
            return literal_eval(val)
        except SyntaxError:
            return None
    converters = {c: convert_string_to_list for c in list_cols}
    results = pd.read_csv(filepath, converters=converters)
    return results

def rerank_paragraphs(paragraph_results_path, save_folder, top_ixs_list_cache_file, top_scores_list_cache_file):
    print()
    paragraph_results = read_pandas_file_with_lists(paragraph_results_path, ["paragraphs"]).set_index("id")
    print(f"Read {len(paragraph_results)} search result samples from '{paragraph_results_path}'.")
    print()
    
    def process_sentences_for_rerank(sentences):
        # truncate too long contexts
        if len(sentences) > RERANK_MAX_NBR_DOCUMENTS:
            sentences = sentences[:RERANK_MAX_NBR_DOCUMENTS]
        return sentences

    print("Getting Cohere rerank scores:")
    
    print("Checking for cache files.")
    top_ixs_list = init_from_cache_file(top_ixs_list_cache_file, as_int=True)
    top_scores_list = init_from_cache_file(top_scores_list_cache_file)
    if len(top_ixs_list) > 0:
        assert len(top_ixs_list) == len(top_scores_list)
        assert len(top_ixs_list[0]) == len(paragraph_results.iloc[0].paragraphs)
    
    start_ix = len(top_ixs_list)
    print(f"Starting from data index {start_ix}")
    for _, row in tqdm(paragraph_results.iloc[start_ix:].iterrows(), total=(len(paragraph_results)-start_ix)):

        paragraphs = process_sentences_for_rerank(row.paragraphs)

        if paragraphs == [""]:
            paragraphs = ["--blank document--"]

        response = co.rerank(
            model="rerank-english-v3.0",
            query=row.claim,
            documents=paragraphs
        )
        top_ixs = [res.index for res in response.results]
        print_list_to_csv_file(top_ixs, top_ixs_list_cache_file)
        top_ixs_list.append(top_ixs)
        
        top_scores = [res.relevance_score for res in response.results]
        print_list_to_csv_file(top_scores, top_scores_list_cache_file)
        top_scores_list.append(top_scores)
        
        # trial key: can at most make 10 requests to the Cohere reranker per minute
        # production key: can at most make 1000 calls per minute
        time.sleep(0.1)

    paragraph_results["top_sent_ix"] = top_ixs_list
    paragraph_results["top_sent_scores"] = top_scores_list
    print("Done!")

    def has_low_rerank_scores(scores):
        return scores[0] < RERANK_SCORE_THRESHOLD

    orig_len = len(paragraph_results)
    low_score_mask = paragraph_results.top_sent_scores.apply(has_low_rerank_scores)
    paragraph_results = paragraph_results[~(low_score_mask)]
    print(f"{orig_len-len(paragraph_results)} (out of {orig_len}) search results removed due to too low reranker scores")
    print(f"{len(paragraph_results)} samples remain.")

    save_file = os.path.join(save_folder, "reranked_paragraph_results.csv")
    paragraph_results.to_csv(save_file)
    print(f"Done! The reranked paragraph results have been saved to '{save_file}'.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rerank search result paragraphs script")
    parser.add_argument("--paragraph_results_path", type=str, required=True, help="Path to the paragraph results CSV file")
    parser.add_argument("--save_folder", type=str, required=True, help="Folder to save the data to")
    parser.add_argument("--top_ixs_list_cache_file", type=str, required=True, help="Cache file for Cohere rerank ix")
    parser.add_argument("--top_scores_list_cache_file", type=str, required=True, help="Cache file for Cohere rerank scores")
    
    args = parser.parse_args()
    
    results_file = os.path.join(args.save_folder, "reranked_paragraph_results.csv")
    if os.path.isfile(results_file):
        print(f"A results file already exists for this script. ('{results_file}')")
        print("Remove it if you want to rerun the script.")
    else:
        os.makedirs(args.save_folder, exist_ok=True)
        rerank_paragraphs(args.paragraph_results_path, 
                        args.save_folder, 
                        args.top_ixs_list_cache_file, 
                        args.top_scores_list_cache_file)