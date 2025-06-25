import os
from nltk import ngrams
from nltk.metrics.distance import jaccard_distance
import stanza

from src.utils import read_txt_file

FACT_CHECK_SITES_FILEPATH = "data/property_detection/fact_check_sites.txt"
MBFC_FOLDER = "data/property_detection/mbfc/"

HEDGE_DETECTION_DATA_FOLDER = "data/property_detection/hedge_detection"

class FactCheckDetector:
    def __init__(self):
        self.fact_check_sites = read_txt_file(FACT_CHECK_SITES_FILEPATH)

    def is_fact_check_article(self, link):
        # content can be full page content (preferable) or the current evidence if the full site content is not available
        if (self.is_fact_check_site(link)) or ("fact-check" in link) or ("factcheck" in link) or ("politifact" in link) or ("misinformation" in link):
            return True
        return False 

    def is_fact_check_site(self, link):
        return any([site.replace("*","").replace("www.","") in link for site in self.fact_check_sites])
    
    
# remove http, https, www., can be after () or - or straight, always with a period, lowercase! check for no conflict

class UnreliableDetector:
    def __init__(self):
        self.fact_cats = ["conspiracy_pseudoscience",
                             "pro_science",
                             "questionable_sources",
                             "satire"]
        self.bias_cats = ["least_biased",
                          "left_bias",
                          "left_center_bias",
                          "right_bias",
                          "right_center_bias"]
        
        self.fact_sites = {c: self.read_mbfc_file(f"{MBFC_FOLDER}/{c}.txt") for c in self.fact_cats}
        self.bias_sites = {c: self.read_mbfc_file(f"{MBFC_FOLDER}/{c}.txt") for c in self.bias_cats}
        
    def read_mbfc_file(self, filepath):
        entries = read_txt_file(filepath)
        # get the urls from the list entries, should contain a period
        url_list = []
        for e in entries:
            url = None
            for t in e.split():
                if "." in t:
                    url = t.lower().replace("(","").replace(")","").replace("https://","").replace("http://","").replace("www.","")
            if url is None:
                raise ValueError(f"No url found in entry '{e}' in file '{filepath}'")
            url_list.append(url)
        return url_list
    
    def get_fact_cat(self, link):
        assert isinstance(link, str)
        for cat, sites in self.fact_sites.items():
            for site in sites:
                if site in link:
                    return cat
        return None
    
    def get_bias_cat(self, link):
        assert isinstance(link, str)
        for cat, sites in self.bias_sites.items():
            for site in sites:
                if site in link:
                    return cat
        return None
    
def read_hedge_detector_file(filename):
    res = []
    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if (not "#" in line) and (len(line)>0):
                res.append(line)
    return res
# implementation based on "A Lexicon-Based Approach for Detecting Hedges in Informal Text"
# https://aclanthology.org/2020.lrec-1.380.pdf
class HedgeDetector():
    def __init__(self):
        self.discourse_markers = read_hedge_detector_file(os.path.join(HEDGE_DETECTION_DATA_FOLDER, "discourse_markers.txt"))
        self.hedge_words = read_hedge_detector_file(os.path.join(HEDGE_DETECTION_DATA_FOLDER, "hedge_words.txt"))
        self.booster_words = read_hedge_detector_file(os.path.join(HEDGE_DETECTION_DATA_FOLDER, "booster_words.txt"))
        # consider up to 7-grams
        self.max_num_grams = 7
        
        self.nlp_pipeline = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse', download_method=None)
        self.nlp_tokenize_pipeline = stanza.Pipeline(lang='en', processors='tokenize,mwt,lemma', download_method=None)
        
        self.processed_discourse_markers = [set([w.lemma.lower() for w in self.nlp_tokenize_pipeline(dm).sentences[0].words]) for dm in self.discourse_markers]
        
    def is_true_hedge_term(self, t, word_ix, sent):
        # TODO: check effect of stemming compared to tokens!
        if t in ["feel", "suggest", "believe", "consider", "doubt", "guess", "hope"]:
            if sent.words[word_ix].head==0 and sent.words[word_ix].xpos[:2]=="VB":
                for w in sent.words:
                    if w.text.lower() in ["we", "i"] and w.head-1 == word_ix and w.deprel=="nsubj":
                        return True
            return False

        if t == "think":
            if sent.words[word_ix+1].xpos=="IN":
                return False
            return True
        
        if t == "assume":
            for w in sent.words:
                if w.head-1 == word_ix and w.deprel=="ccomp":
                    return True
            return False
        
        if t == "suppose":
            for xcomp_ix, w in enumerate(sent.words):
                if w.head-1 == word_ix and w.deprel=="xcomp":
                    for sub_w in sent.words:
                        if sub_w.head-1 == xcomp_ix and sub_w.deprel=="mark" and sub_w.xpos=="TO":
                            return False
            return True
        
        if t == "tend":
            for w in sent.words:
                if w.head-1 == word_ix and w.deprel=="xcomp":
                    return True
            return False
        
        if t == "appear":
            for w in sent.words:
                if w.head-1 == word_ix and (w.deprel=="ccomp" or w.deprel=="xcomp"):
                    return True
            return False
        
        # not working
        # if t == "likely":
        #     if sent.words[word_ix].deprel == "advmod" and sent.words[sent.words[word_ix].head-1].xpos[0] == "N":
        #         return False
        #     return True
        
        # removed as a hedge word
        # if t == "should":
        #     if sent.words[word_ix].deprel == "aux":
        #         head_ix = sent.words[word_ix].head
        #         for w in sent.words:
        #             if w.head == head_ix and w.deprel == "have":
        #                 return False
        #     return True
        
        if t == "rather":
            if sent.words[word_ix+1].lemma == "than":
                return False
            return True
        
        return True
        
    def is_hedged_text(self, text):
        doc = self.nlp_pipeline(text)
        
        found_discourse_markers = False
        found_hedge_terms = False
        found_boosters_preceeded_by_negation = False
        
        for sent in doc.sentences:
            words = [w.lemma.lower() for w in sent.words]
            # hedge detection based on discourse markers
            max_num_grams = min(len(words), self.max_num_grams)
            grams = []
            for i in range(1, max_num_grams+1):
                grams.extend(ngrams(words, i))
            for dm_set in self.processed_discourse_markers:
                for ng in grams:
                    if 1-jaccard_distance(dm_set, set(ng)) >= 0.8:
                        found_discourse_markers = True
                        break
                    
            # hedge detection based on hedge terms
            for hw in self.hedge_words:
                try:
                    if hw in words and self.is_true_hedge_term(hw, words.index(hw), sent):
                        found_hedge_terms = True
                        break
                except Exception as e:
                    print(f"Error when processing hedge word {hw} for text '{text}':")
                    print(e)
                    found_hedge_terms = None
                    break
            
            # hedge detection based on boosters preceeded by negation
            for bw in self.booster_words:
                if bw in words:
                    bw_index = words.index(bw)
                    if bw_index > 0:
                        prev_word = words[bw_index-1]
                        if prev_word == "not" or prev_word == "without":
                            found_boosters_preceeded_by_negation = True
                            break
            
        return found_discourse_markers, found_hedge_terms, found_boosters_preceeded_by_negation
