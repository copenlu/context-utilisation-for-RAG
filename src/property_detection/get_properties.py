# move stuff from notebook to here
from pathlib import Path
import os
from urllib.parse import urlparse
import pandas as pd
import numpy as np
import spacy
from matplotlib import pyplot as plt
from textstat import flesch_reading_ease
from nltk.metrics.distance import jaccard_distance
from nltk.tokenize import word_tokenize
from string import punctuation
from tqdm import tqdm

from src.property_detection.property_detectors import FactCheckDetector, UnreliableDetector, HedgeDetector
from src.utils import print_data_to_txt_file

SKIPLIST = set(list(punctuation) + ["”", "“", "—", "’", "``", "''"])

def get_unreliable_mbfc(data):
    evidence_sources = data.evidence_source.tolist()
    
    unreliable_detector = UnreliableDetector()
    mbfc_bias_cat = list(map(unreliable_detector.get_bias_cat, evidence_sources))
    mbfc_fact_cat = list(map(unreliable_detector.get_fact_cat, evidence_sources))

    def get_domain(evidence_source):
        return urlparse(evidence_source).netloc

    def is_gov_page(evidence_source):
        domain = get_domain(evidence_source)
        return domain.endswith(".gov") or ".gov." in domain
    is_gov_pages = list(map(is_gov_page, evidence_sources))

    def is_edu_page(evidence_source):
        domain = get_domain(evidence_source)
        return domain.endswith(".edu")
    is_edu_pages = list(map(is_edu_page, evidence_sources))

    def is_unreliable_mbfc_gov_edu(mbfc_bias_cat, mbfc_fact_cat, is_gov_page, is_edu_page):
        if (mbfc_bias_cat is None) and (mbfc_fact_cat is None):
            if is_gov_page or is_edu_page:
                return False
            else:
                return None
        if (mbfc_fact_cat is not None and mbfc_fact_cat in ["questionable_sources", "conspiracy_pseudoscience", "satire"]):
            return True
        if (mbfc_bias_cat is not None and mbfc_bias_cat in ["left_bias", "righ_bias"]):
            return True
        return False                           

    return list(map(is_unreliable_mbfc_gov_edu, mbfc_bias_cat, mbfc_fact_cat, is_gov_pages, is_edu_pages))

def get_is_factcheck_article(data):
    evidence_sources = data.evidence_source.tolist()
    fact_check_detector = FactCheckDetector()
    
    is_factcheck_article = list(map(fact_check_detector.is_fact_check_article, evidence_sources))
    
    # Check if any fact-check sites have been missed
    url_sites_fact = data[~(np.array(is_factcheck_article))]\
        .evidence_source[data.evidence_source.apply(lambda val: "fact" in val)].unique()
    check_url_sites_fact = list(set([urlparse(url).netloc.replace("www.","") for url in url_sites_fact]))
    check_url_sites_fact.extend(list(set([url.replace("www.","") for url in url_sites_fact])))
    missed_fact_filepath = "tmp_potentially_missed_fc_sites.txt"
    print_data_to_txt_file(check_url_sites_fact, missed_fact_filepath)
    print(f"Potential fact-check sites that haven't been detected have been saved to '{missed_fact_filepath}'.")
    print()
    
    return is_factcheck_article

def get_claim_entity_overlap(data):
    # a rate of 0 equals not implicit
    # a rate of 1 equals fully implicit
    def get_implicit_level(e1, e2):
        if len(e1) == 0:
            return None
        # calculate how many of e1 entities can be found in e2
        return len(e1.intersection(e2))/len(e1)
        
    spacy.require_gpu() # TODO: uncomment for GPU
    ner = spacy.load("en_core_web_trf") # TODO: set to 'en_core_web_trf' for GPU (roberta-base for NER)
    claim_entities = list(map(lambda val: set([ent.text.lower() for ent in ner(val).ents]), data.claim.tolist()))
    evidence_entities = list(map(lambda val: set([ent.text.lower() for ent in ner(val).ents]), data.evidence.tolist()))
    return list(map(get_implicit_level, claim_entities, evidence_entities))

def get_flesch_reading_ease_score(data):
    return data.evidence.apply(flesch_reading_ease)

def get_uncertain_rate_lexicon(data):
    hedge_detector = HedgeDetector()
    tqdm.pandas() # to get a progress bar
    data[["uncertain_discourse_markers", "uncertain_hedge_terms", "uncertain_boosters_preceeded_by_negation"]] = data.evidence.progress_apply(hedge_detector.is_hedged_text).tolist()
    return {"uncertain_discourse_markers": data["uncertain_discourse_markers"].tolist(),
            "uncertain_hedge_terms": data["uncertain_hedge_terms"].tolist(),
            "uncertain_boosters_preceeded_by_negation": data["uncertain_boosters_preceeded_by_negation"].tolist()}

def get_jaccard_sim(data):
    def get_jaccard_index(s1, s2):
        words_1 = set([w.lower() for w in word_tokenize(s1) if w.lower() not in SKIPLIST])
        words_2 = set([w.lower() for w in word_tokenize(s2) if w.lower() not in SKIPLIST])
        return 1-jaccard_distance(words_1, words_2)

    return list(map(get_jaccard_index, data.claim, data.evidence))

def get_claim_repeated_in_evidence(data):
    def string_in_doc(s, doc):
        s_words = (" ").join([w.lower() for w in word_tokenize(s) if w.lower() not in SKIPLIST])
        doc_words = (" ").join([w.lower() for w in word_tokenize(doc) if w.lower() not in SKIPLIST])
        return s_words in doc_words
        
    return list(map(string_in_doc, data.claim, data.evidence))

def get_evidence_length(data):
    return data.evidence.apply(len)

def get_claim_length(data):
    return data.claim.apply(len)

PROPERTY_FUNS = {"unreliable_mbfc": get_unreliable_mbfc,
                 "is_factcheck_article": get_is_factcheck_article,
                 "claim_entity_overlap": get_claim_entity_overlap,
                 "flesch_reading_ease_score": get_flesch_reading_ease_score,
                 "uncertain_rate_lexicon": get_uncertain_rate_lexicon,
                 "claim_evidence_jaccard_sim": get_jaccard_sim,
                 "claim_repeated_in_evidence": get_claim_repeated_in_evidence,
                 "evidence_length": get_evidence_length,
                 "claim_length": get_claim_length}

if __name__ == "__main__":    
    import argparse
    parser = argparse.ArgumentParser(description="Auto detect properties for DRUUID.")
    parser.add_argument("--data_path", type=str, help="Path to .tsv file with data to detect properties for. Should contain the columns 'evidence', 'claim' and 'evidence_source'.")
    parser.add_argument("--save_folder", type=str, help="Folder to save the results (data with properties) to.")
    parser.add_argument("--properties", type=str, help="String with properties to detect, separated by spaces. Choose either 'all' or a set of properties (from PROPERTY_FUNS in the code).")
    
    args = parser.parse_args()
    
    Path(args.save_folder).mkdir(exist_ok=True)
    
    data = pd.read_csv(args.data_path, sep="\t").set_index("id")
    print(f"{len(data)} samples loaded.")
    print()

    if args.properties == "all":
        properties = PROPERTY_FUNS.keys()
    else:
        properties = args.properties.split()
        
    for prop in properties:
        print(f"Processing property {prop}...")
        save_file = os.path.join(args.save_folder, f"tmp_{prop}.tsv")
        res = PROPERTY_FUNS[prop](data)
        if isinstance(res, dict):
            for key, val in res.items():
                data[key] = val
            prop_cols = list(res.keys())
        else:
            data[prop] = res
            prop_cols = [prop]
        data[prop_cols].to_csv(save_file, sep="\t")
        print(f"Processing of {prop} done! Saved checkpoint to '{save_file}'.")
        print()
        print("Short statistics:")
        if len(prop_cols) > 1 or len(data[prop].unique()) < 5:
            # use value counts if not so many properties
            print(data.value_counts(prop_cols, sort=False, dropna=False))
        else:
            data[prop].hist()
            plt.xlabel(prop)
            plt.ylabel("Counts")
            filename = os.path.join(args.save_folder, f"{prop}_hist.pdf")
            plt.savefig(filename)
            plt.clf()
            print(f"Statistics saved to {filename}.")
        print()
    
    save_file = os.path.join(args.save_folder, "data_with_properties.tsv")
    data.to_csv(save_file, sep="\t")
    print(f"Done! Saved data with properties to '{save_file}'.")