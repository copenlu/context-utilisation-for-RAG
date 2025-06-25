import os
from datetime import datetime
import pandas as pd
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from string import punctuation

from src.retrieval.rerank_paragraphs import read_pandas_file_with_lists, RERANK_SCORE_THRESHOLD
from src.property_detection import FactCheckDetector

EVIDENCE_PUBLISHED_AFTER_CLAIM_MONTH_DIFF = 1 # min months before the claim date for which the evidence has to be published to not be classified as published after claim
MAX_WORDS_IN_EVIDENCE = 300

def word_count_similarity(claim, doc):
    SKIPLIST = set(list(punctuation) + ["”", "“", "—", "’", "``", "''"])
    claim_words = set([w.lower() for w in word_tokenize(claim) if w.lower() not in SKIPLIST])
    doc_words = set([w.lower() for w in word_tokenize(doc) if w.lower() not in SKIPLIST])
    if len(doc_words) > 0:
        return len(claim_words.intersection(doc_words))/len(doc_words)
    else:
        return 0 

def claim_is_majority_of_doc(claim, doc, threshold):
    return word_count_similarity(claim, doc) > threshold
        
def agg_top_paragraphs(row, max_n_context, max_paragraph_neighbour_dist, claim_is_majority_of_doc_theshold):
    # only keep sentence indeces corresponding to a sufficient score and no exact claim repetition
    top_ixs = []
    num_ix = 0
    num_words = 0
    for ix, score in zip(row.top_sent_ix, row.top_sent_scores):
        # stop if we are below the score threshold or already have all necessary sentences or have exceeded word limit
        if score > RERANK_SCORE_THRESHOLD and num_ix < max_n_context and num_words < MAX_WORDS_IN_EVIDENCE:
            if not claim_is_majority_of_doc(row.claim, row.paragraphs[ix], claim_is_majority_of_doc_theshold):
                top_ixs.append(ix)
                num_ix += 1
                num_words += len(word_tokenize(row.paragraphs[ix]))
        else:
            break
    
    # we might already have overshot the max word limit, need to remove the last top index if so
    if num_words > MAX_WORDS_IN_EVIDENCE:
        top_ixs = top_ixs[:-1]
    
    if len(top_ixs) == 0:
        return None
        
    top_ixs = sorted(top_ixs)
    context = row.paragraphs[top_ixs[0]]
    for ix in range(len(top_ixs)-1):
        # if retrieved sentences are located close to each other
        # also fetch the information in between.
        if (top_ixs[ix+1]-top_ixs[ix]) <= max_paragraph_neighbour_dist:
            context = context + " " + (" ").join(row.paragraphs[top_ixs[ix]+1:top_ixs[ix+1]+1])
        # otherwise, merge with a "[...]" in between
        else:
            context = context + " [...] " + row.paragraphs[top_ixs[ix+1]]
    return context
    
def diff_month(d1, d2):
    d1 = datetime.strptime(d1, '%Y-%m-%d')
    d2 = datetime.strptime(d2, '%Y-%m-%d')
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def get_evidence_from_reranked_paragraphs(reranked_paragraphs_path, 
                                          save_folder, 
                                          source_claims_path,
                                          max_paragraphs_in_evidence,
                                          max_claims_after_date,
                                          max_paragraph_neighbour_dist,
                                          evidence_per_claim,
                                          claim_is_majority_of_doc_theshold):
    print()
    search_results = read_pandas_file_with_lists(reranked_paragraphs_path, 
                                                 ["paragraphs", "top_sent_ix", "top_sent_scores"]).set_index("id")
    print(f"Read {len(search_results)} samples from '{reranked_paragraphs_path}'.")
    print()

    print("Adding metadata from source claims (claim date and claimant):")
    search_results = search_results.rename(columns={"url_date": "evidence_date"})
    source_data = pd.read_csv(source_claims_path).set_index("id")
    search_results["claim_date"] = search_results.claim_id.map(lambda val: source_data.loc[val].date)
    search_results["claimant"] = search_results.claim_id.map(lambda val: source_data.loc[val].claimant)
    print()
    
    print("Aggregating paragraphs to get evidence")
    search_results["evidence"] = search_results.apply(lambda row: 
        agg_top_paragraphs(row, max_paragraphs_in_evidence, max_paragraph_neighbour_dist, claim_is_majority_of_doc_theshold), axis=1)
    search_results = search_results.drop_duplicates(["claim", "evidence"]).dropna(axis=0, subset=["evidence"])

    search_results["top_sent_score"] = search_results.top_sent_scores.apply(lambda val: val[0]) # use this to select documents
    keep_id = []
    for claim_id in tqdm(search_results.claim_id.unique()):
        partition = search_results[search_results.claim_id==claim_id].copy()
        # # keep only a subset of fact checking articles
        # drop_factcheck_ix = partition[partition.is_fact_check_article].sort_values(by="top_sent_score", ascending=False).iloc[MAX_FACT_CHECK_SOURCES:].index
        # partition = partition.drop(drop_factcheck_ix)
        
        if max_claims_after_date is not None:
            # keep only a subset of articles published after the claim date (1 month margin)
            evidence_published_after_claim_mask = partition.apply(lambda row: diff_month(row.claim_date, row.evidence_date)<EVIDENCE_PUBLISHED_AFTER_CLAIM_MONTH_DIFF, axis=1)
            drop_after_date_ix = partition[evidence_published_after_claim_mask].sort_values(by="top_sent_score", ascending=False).iloc[max_claims_after_date:].index
            partition = partition.drop(drop_after_date_ix)
        
        if evidence_per_claim is not None:
            if len(partition) >= evidence_per_claim:
                keep_id.extend(partition.sort_values(by="top_sent_score", ascending=False).iloc[:evidence_per_claim].index.tolist())
        else:
            # keep all evidence pieces
            keep_id.extend(partition.sort_values(by="top_sent_score", ascending=False).index.tolist())

    search_results = search_results.loc[keep_id]
    print(f"{evidence_per_claim} evidence pieces found for {len(search_results.claim_id.unique())} claims.")
    print()
    if len(search_results)==0:
        print(f"Error: no claims found corresponding to {evidence_per_claim} evidence pieces per claim with the current config.")
        return
    
    print(f"Distribution of number of fact check articles as evidence (out of {evidence_per_claim}) per claim:")
    fact_check_detector = FactCheckDetector()
    search_results["is_fact_check_article"] = search_results.apply(lambda row: fact_check_detector.is_fact_check_article(row.link), axis=1)
    print(search_results.groupby(["claim_id"]).is_fact_check_article.count().value_counts())
    print()
    
    print("Distribution of evidence published after the claim date:")
    search_results["evidence_published_after_claim"] = search_results.apply(lambda row: diff_month(row.claim_date, row.evidence_date)<EVIDENCE_PUBLISHED_AFTER_CLAIM_MONTH_DIFF, axis=1)
    print(search_results.groupby(["claim_id"]).evidence_published_after_claim.count().value_counts())
    print()
    
    print("Dropping long columns (paragraphs, cohere reranker scores) for simplicity.")
    search_results = search_results.drop(columns=["paragraphs", "top_sent_ix", "top_sent_scores","top_sent_score"])
    print()
    
    save_file = os.path.join(save_folder, "evidence_results.csv")
    search_results.to_csv(save_file)
    print(f"Done! A total of {len(search_results)} crawled search results have been saved to '{save_file}'.")
    

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get evidence from reranked paragraphs script")
    parser.add_argument("--reranked_paragraphs_path", type=str, required=True, help="Path to the reranked paragraphs CSV file")
    parser.add_argument("--save_folder", type=str, required=True, help="Folder to save the data to")
    parser.add_argument("--source_claims_path", type=str, required=True, help="Path to source claims CSV file")
    parser.add_argument("--max_paragraphs_in_evidence", type=int, default=2, help="Maximum number of paragraphs allowed for one evidence piece")
    parser.add_argument("--max_claims_after_date", type=int, default=None, help="Maximum number of evidence allowed to have been published after the claim date")
    parser.add_argument("--max_paragraph_neighbour_dist", type=int, default=1, help="Maximum number of in-between neighbours allowed for merged concatenation of paragraphs")
    parser.add_argument("--evidence_per_claim", type=int, default=None, help="Number of evidence pieces that should be fetched per claim")
    parser.add_argument("--claim_is_majority_of_doc_theshold", type=float, default=0.8, help="Threshold for when to define evidence as too similar to the claim")
    
    args = parser.parse_args()
    
    results_file = os.path.join(args.save_folder, "evidence_results.csv")
    if os.path.isfile(results_file):
        print(f"A results file already exists for this script. ('{results_file}')")
        print("Remove it if you want to rerun the script.")
    else:
        os.makedirs(args.save_folder, exist_ok=True)
        get_evidence_from_reranked_paragraphs(args.reranked_paragraphs_path, 
                                            args.save_folder,
                                            args.source_claims_path,
                                            args.max_paragraphs_in_evidence,
                                            args.max_claims_after_date,
                                            args.max_paragraph_neighbour_dist,
                                            args.evidence_per_claim,
                                            args.claim_is_majority_of_doc_theshold)