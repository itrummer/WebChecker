'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import pandas as pd
import time
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from urllib.request import urlopen

def google_query(query_one, api_key, cse_id):
    """ Uses specified search engine to query_one, returns results. 
    
    Returns:
        A list of search result items.
    """
    query_service = build(
        "customsearch", "v1", developerKey=api_key)
    all_results = []
    for start in range(1, 10, 10):
        print(f'Retrieving results starting from index {start}')
        query_results = query_service.cse().list(
            q=query_one, cx=cse_id, start=start, lr='lang_en').execute()
        nr_results = int(query_results['searchInformation']['totalResults'])
        print(f'Web query retrieved {nr_results} results')
        if nr_results > 0:
            all_results += query_results['items']
    return all_results

# def get_web_text(url):
    # """ Extract text passages from given URL body. 
    #
    # Returns:
        # Lines from Web site or None if not retrievable.
    # """
    # try:
        # html_src = urlopen(url, timeout=5).read()
        # print(f'Retrieved url {url}')
        # return extract_text(html_src)
    # except:
        # return []

def can_parse(result):
    """ Returns true iff the search result can be used. """
    return True if not '.pdf' in result['link'] else False

def extract_text(html_src):
    """ Extract text passages from given URL body. 
    
    Args:
        html_src: HTML source code for text extraction.
        
    Returns:
        Lines from Web site or None if not retrievable.
    """
    try:
        print(f'Parsing HTML with length {len(html_src)} ...')
        start_s = time.time()
        parsed = BeautifulSoup(html_src, features="html.parser")
        for script in parsed(["script", "style"]):
            script.extract()
        text = parsed.get_text()
        total_s = time.time() - start_s
        print(f'Parsed text with length {len(text)} in {total_s}s.')
        
        start_s = time.time()
        lines = [line.strip() for line in text.splitlines()]
        clean_lines = []
        for line in lines:
            clean_lines += [part.strip() for part in line.split("  ")]
        clean_lines = [line for line in clean_lines if len(line)>2]
        total_s = time.time() - start_s
        print(f'Extracted {len(clean_lines)} lines in {total_s}s')
        
        start_s = time.time()
        full_text = " ".join(clean_lines)
        sentences = full_text.split('.')
        total_s = time.time() - start_s
        print(f'Generated sentences in {total_s}s')
        return sentences
    
    except Exception as e:
        print(f'Exception during extraction: {e}')
        return []

class Access():
    """ Wrapper for Web querying via Google search. """
    
    def __init__(self, key, cse):
        """ Initialize class by storing credentials. 
                
        Args:
            key: Google API key
            cse: search engine ID
        """
        self.key = key
        self.cse = cse
    
    def gsearch(self, query, web_filter, timeout_s):
        """ Retrieves single sentences from result of Google search.
        
        Args:
            query: retrieve results for this Google query
            web_filter: whether to filter long documents
            timeout_s: retrieval timeout in seconds
            
        Returns:
            data frame containing result lines with file IDs
        """
        start_s = time.time()
        print(f'Issuing query {query}; filter flag: {web_filter}')
        items = google_query(query, self.key, self.cse)
        rows = []
        for docid, result in enumerate(items):
            url = result['link']
            print(url)
            
            if can_parse(result):
                print('Processing document')
                try:
                    html_src = urlopen(url, timeout=2).read()
                    print(f'Retrieved url {url}')
                    if not web_filter or len(html_src) < 100000:
                        print(f'Passes Web filter')
                        lines = extract_text(html_src)
                        for line in lines:
                            rows.append([docid, url, line])
                except Exception as e:
                    print(f'Exception during retrieval: {e}')
            else:
                print('Did not process document')
            
            total_s = time.time() - start_s
            if total_s > timeout_s:
                break
                
        return pd.DataFrame(rows, columns=['filenr', 'url', 'sentence'])
    
    def match_triple(self, triple, web_idx, web_filter, timeout_s):
        """ Retrieves Web sentences that may match given triple. 
        
        Args:
            triple: subject, predicate, object used for Web query
            web_idx: how to construct query from triple
            web_filter: whether to filter Web result further
            timeout_s: retrieval timeout in seconds
            
        Returns:
            Web sentences related to triple
        """
        subj, pred, obj = triple
        if web_idx == 0:
            query = subj + ' ' + pred + ' ' + obj
        else:
            query = '"' + subj + '" ' + pred + ' "'  + obj + '"'
        
        sentences = self.gsearch(query, int(web_filter), timeout_s)
        # if web_filter == 1:
            # short = sentences.apply(lambda r:len(r['sentence'])<100, axis=1)
            # sentences = sentences[short]
        return sentences