#!/usr/bin/env bash

# normal cpu stuff: allocate cpus, memory
#SBATCH --ntasks=1 --cpus-per-task=10 --mem=40000MB
# we run on the gpu partition and we allocate 2 titanx gpus
#SBATCH -p gpu
#We expect that our program should not run longer than 4 hours
#Note that a program will be killed once it exceeds this time!
#SBATCH --time=1-00:00:00

SAVE_FOLDER=$1

set -e

echo "Starting full retrieval pipeline."
echo "Source claims will be read from '${SAVE_FOLDER}/gold_samples.csv'"
echo "All results will be stored in '${SAVE_FOLDER}'"
echo

echo "Collecting search results:"
RESULTS_FILE="${SAVE_FOLDER}/search_results.csv"
if [ -f $RESULTS_FILE ]; then
    echo "A results file already exists for this script. ('${RESULTS_FILE}')"
    echo "Remove it if you want to rerun the script."
else
    python -m src.retrieval.get_search_results \
        --source_claims_path "${SAVE_FOLDER}/gold_samples.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --num_search_results 20
fi
echo

echo "Crawling search results:"
RESULTS_FILE="${SAVE_FOLDER}/crawl_results.csv"
if [ -f $RESULTS_FILE ]; then
    echo "A results file already exists for this script. ('${RESULTS_FILE}')"
    echo "Remove it if you want to rerun the script."
else
    python -m src.retrieval.crawl_search_results \
        --search_results_path "${SAVE_FOLDER}/search_results.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --crawled_pages_cache_path "${SAVE_FOLDER}/crawled_pages.csv"
fi
echo

echo "Extracting paragraphs from crawled content:"
RESULTS_FILE="${SAVE_FOLDER}/paragraph_results.csv"
if [ -f $RESULTS_FILE ]; then
    echo "A results file already exists for this script. ('${RESULTS_FILE}')"
    echo "Remove it if you want to rerun the script."
else
    python -m src.retrieval.get_paragraphs_from_crawl \
        --crawl_results_path "${SAVE_FOLDER}/crawl_results.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --min_word_limit 4 \
        --max_word_limit 200 \
        --clean_sentence_method "word_count"
fi
echo

echo "Getting rerank scores for paragraphs:"
RESULTS_FILE="${SAVE_FOLDER}/reranked_paragraph_results.csv"
if [ -f $RESULTS_FILE ]; then
    echo "A results file already exists for this script. ('${RESULTS_FILE}')"
    echo "Remove it if you want to rerun the script."
else
    python -m src.retrieval.rerank_paragraphs \
        --paragraph_results_path "${SAVE_FOLDER}/paragraph_results.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --top_ixs_list_cache_file "${SAVE_FOLDER}/top_ixs_cache.csv" \
        --top_scores_list_cache_file "${SAVE_FOLDER}/top_scores_cache.csv" 
fi
echo

echo "Getting evidence from reranked paragraphs:"
RESULTS_FILE="${SAVE_FOLDER}/evidence_results.csv"
if [ -f $RESULTS_FILE ]; then
    echo "A results file already exists for this script. ('${RESULTS_FILE}')"
    echo "Remove it if you want to rerun the script."
else
    python -m src.retrieval.get_evidence_from_reranked_paragraphs \
        --reranked_paragraphs_path "${SAVE_FOLDER}/reranked_paragraph_results.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --source_claims_path "${SAVE_FOLDER}/gold_samples.csv" \
        --max_paragraphs_in_evidence 3 \
        --max_claims_after_date 2 \
        --max_paragraph_neighbour_dist 1 \
        --evidence_per_claim 4
fi
echo

echo "Getting dataset to annotate from auto retrieved results and source claims data"
RESULTS_FILE="${SAVE_FOLDER}/dataset_to_annotate_1.tsv"
if [ -f $RESULTS_FILE ]; then
    echo "A results file already exists for this script. ('${RESULTS_FILE}')"
    echo "Remove it if you want to rerun the script."
else
    python -m src.retrieval.get_dataset_to_annotate \
        --auto_evidence_path "${SAVE_FOLDER}/evidence_results.csv" \
        --source_claims_path "${SAVE_FOLDER}/gold_samples.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --n_claims 220 \
        --n_claims_per_batch 44
fi
echo

echo "Full retrieval completed!"