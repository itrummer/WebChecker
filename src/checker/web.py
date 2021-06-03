'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import pandas as pd
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

def get_web_text(url):
    """ Extract text passages from given URL body. 
    
    Returns:
        Lines from Web site or None if not retrievable.
    """
    try:
        html_src = urlopen(url, timeout=5).read()
        print(f'Retrieved url {url}')
        return extract_text(html_src)
    except:
        return []

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
        parsed = BeautifulSoup(html_src, features="html.parser")
        for script in parsed(["script", "style"]):
            script.extract()
        text = parsed.get_text()
        print(f'Parsed text with length {len(text)}.')
        
        lines = [line.strip() for line in text.splitlines()]
        clean_lines = []
        for line in lines:
            clean_lines += [part.strip() for part in line.split("  ")]
        clean_lines = [line for line in clean_lines if len(line)>2]
        print(f'Extracted {len(clean_lines)} lines')
        
        full_text = " ".join(clean_lines)
        sentences = full_text.split('.')
        return sentences
    
    except Exception as e:
        print(f'Exception during extraction: {e}')
        return []
    
def gsearch_lines(query, key, cse):
    """ Retrieves single lines from result of Google search.
    
    Args:
        query: retrieve results for this Google query
        key: Google API key
        cse: search engine ID
        
    Returns:
        data frame containing result lines with file IDs
    """
    items = google_query(query, key, cse)
    rows = []
    for docid, result in enumerate(items):
        url = result['link']
        print(url)
        if can_parse(result):
            print('Processing document')
            lines = get_web_text(url)
            for line in lines:
                rows.append([docid, line])
        else:
            print('Did not process document')
    return pd.DataFrame(rows, columns=['filenr', 'sentence'])