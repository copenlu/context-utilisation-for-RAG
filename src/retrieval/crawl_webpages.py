import os
import time
from urllib.parse import urlparse
import csv
import threading
import queue
import requests
from trafilatura import fetch_url, extract
from htmldate import find_date
import justext
import pandas as pd
from protego import Protego
from tqdm import tqdm

HEADERS = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language' : 'en-GB,en;q=0.5'
}
STANDARD_CRAWL_DELAY = 1

def does_url_exist(url):
    r = requests.head(url, timeout=10)
    if r.status_code < 400:
        return True
    else:
        return False

def crawl_webpage(url):
    trafilatura_success = False
    downloaded = fetch_url(url)
    if downloaded is not None:
        textual_content = extract(downloaded, 
                                  include_comments=False, 
                                  include_tables=False, 
                                  favor_precision = False, 
                                  favor_recall=False, 
                                  deduplicate=True,
                                  url=url)
        publish_date = find_date(downloaded)
        
        # check for paragraph issues
        # previously had an issue with a paragraph of length 982056
        if textual_content is not None:
            paragraphs = textual_content.splitlines()
            trafilatura_success = not (len(paragraphs)==1 and len(paragraphs[0])>10000)
        else:
            trafilatura_success = False
    
    # try another method if the trafilatura approach does not work
    if not trafilatura_success:
        textual_content, publish_date = crawl_webpage_with_requests(url)
    return textual_content, publish_date
    
# fallback alternative using requests instead of trafilatura
def crawl_webpage_with_requests(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=120)
        status_code = resp.status_code
        if status_code >= 300:
            #print('status code:', status_code)
            return None, None
        paragraphs = justext.justext(resp.text, justext.get_stoplist("English"))
        publish_date = find_date(resp.text)
        return ("\n").join([p.text for p in paragraphs]), publish_date
    except:
        print(f"Error reading with requests - {url}")
        return None, None

class DefaultRules():
    def crawl_delay(self, user):
        return STANDARD_CRAWL_DELAY
    def can_fetch(self, link, user):
        return True
class FaultyDomainRules():
    def crawl_delay(self, user):
        raise ValueError("This is a faulty domain rules set, crawl delay should not be requested for it.")    
    def can_fetch(self, link, user):
        return False
    
def get_crawl_rules(domain):
    # returns the crawl rules for the domain page based on the robots.txt file
    robots_url = 'https://' + domain + '/robots.txt'
    try:
        if does_url_exist(robots_url):
            r = requests.get(robots_url, timeout=10)
            rules = Protego.parse(r.text)
            return rules
        else:
            print(f"Warning: No robots.txt file found at '{robots_url}'. Using default crawl rules for {domain}.")
            return DefaultRules()
    except Exception as e:
        print(f"Failed when fetching rules from '{robots_url}'. Skipping {domain} henceforth.")
        print(e)
        return FaultyDomainRules()

# TODO: do not store crawl results in-memory but to file, then read from file?
class PageCrawler():
    def __init__(self, lookup_file, num_threads=5):
        self.webpage_content = {}
        self.webpage_date = {}
        
        self.lookup_file = lookup_file
        self.init_from_lookup_file()
        
        self.num_threads = num_threads
        self.link_queue = queue.Queue()
        self.last_visit_time = {}
        self.crawl_rules = {}
        self.lock = threading.Lock()

    def init_from_lookup_file(self):
        if not os.path.exists(self.lookup_file):
            # initialize the url-content lookup
            print(f"No url-content-date lookup found. Setting up a new one at '{self.lookup_file}'..")
            with open(self.lookup_file, "w") as f:
                f.write("url,content,date")
                f.write("\n")
        else:
            # load an existing url-content lookup
            print(f"A url-content lookup was found at '{self.lookup_file}'. Loading the entries..")
            tmp = pd.read_csv(self.lookup_file)
            self.webpage_content = {row.url: row.content for _, row in tmp.iterrows()}
            self.webpage_date = {row.url: row.date for _, row in tmp.iterrows()}

    def save_to_lookup_file(self, link, content, date):
        with open(self.lookup_file, 'a') as f:
            w = csv.writer(f, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL, quotechar='"', doublequote=True)
            w.writerow([link,content,date])

    def crawl_page(self, link):
        # skip if the page has already been crawled
        with self.lock:
            if link in self.webpage_content:
                return
        
        domain = urlparse(link).netloc
        with self.lock:
            if domain not in self.crawl_rules:
                self.crawl_rules[domain] = get_crawl_rules(domain)
                
                if self.crawl_rules[domain].can_fetch(link, "*"):
                    crawl_delay = self.crawl_rules[domain].crawl_delay("*")
                    crawl_delay = STANDARD_CRAWL_DELAY if crawl_delay is None else crawl_delay
                    self.last_visit_time[domain] = (0, crawl_delay) # provide both time when last visited and required delay
                
        with self.lock:
            if self.crawl_rules[domain].can_fetch(link, "*"):
                last_visit, crawl_delay = self.last_visit_time[domain]
            else:
                print(f"Warning: not allowed to crawl '{link}'")
                self.webpage_content[link] = None
                self.webpage_date[link] = None
                # store the crawl results in the lookup file
                self.save_to_lookup_file(link, None, None)
                return
        
        elapsed_time = time.time() - last_visit
        wait_time = max(0, crawl_delay - elapsed_time)
        time.sleep(wait_time)
        
        content, date = crawl_webpage(link)
        with self.lock:
            self.last_visit_time[domain] = (time.time(), crawl_delay)
            self.webpage_content[link] = content
            self.webpage_date[link] = date
            # store the crawl results in the lookup file
            self.save_to_lookup_file(link, content, date)
            
    def worker(self, progress_bar):
        while True:
            link = self.link_queue.get()
            if link is None:
                break
            self.crawl_page(link)
            self.link_queue.task_done()
            progress_bar.update(1)
            
    def crawl_pages(self, links):
        progress_bar = tqdm(total=len(links), desc="Crawling pages")
        
        # Add URLs to the queue
        for link in links:
            self.link_queue.put(link)
        
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker, args=(progress_bar,))
            t.start()
            threads.append(t)

        # Block until all tasks are done
        self.link_queue.join()

        # Stop the worker threads
        for _ in range(self.num_threads):
            self.link_queue.put(None)
        for t in threads:
            t.join()
            
        progress_bar.close()