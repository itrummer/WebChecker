'''
Created on Jun 4, 2021

@author: immanueltrummer
'''
import checker.akb
import checker.nlp
import checker.web
import time

class Detector():
    """ Detect misinformation on the Web by processing detection plans. """
    
    def __init__(self, api_key, cse, naf_path, eaf_path, retry_af):
        """ Initialize AKB and web access entailment checks.
        
        Args:
            api_key: API key for Google customized search engine
            cse: Google custom search engine ID
            naf_path: path to number mistakes
            eaf_path: path to entity mistakes
            retry_af: re-try anti-facts with different plans?
        """
        self.web = checker.web.Access(api_key, cse)
        akb_number = checker.akb.Access(naf_path)
        akb_entity = checker.akb.Access(eaf_path)
        self.akbs = [akb_number, akb_entity]
        self.retry_af = retry_af
        self.entail = checker.nlp.EntailmentUtil()
        self.nr_facts = 0
        self.nr_checks = 0
        self.init_s = time.time()
        
    def execute(self, plan, timeout_s):
        """ Try to find Web matches for AKB entries with given plan. 
        
        Args:
            plan: detection plan determining details of matching process
            timeout_s: matching timeout in seconds
            
        Returns:
            Newly discovered matches
        """
        print(f'Evaluating plan {plan}')
        akb_idx = plan[0]
        akb_filter = plan[1]
        web_idx = plan[2]
        web_filter = plan[3]
        ent_seq = plan[4]
        
        retrieval_s = int(timeout_s / 2)
        entailment_s = retrieval_s
        
        req_id = plan[1:] if self.retry_af else [0, 0, 0, 0]
        akb = self.akbs[akb_idx]
        triple = akb.next_triple(req_id, akb_filter)
        af = triple[0] + ' ' + triple[1] + ' ' + triple[2]
        self.nr_facts += 1
        
        web_result = self.web.match_triple(
            triple, web_idx, web_filter, retrieval_s)

        matches = []        
        start_s = time.time()
        for row in web_result.itertuples():
            
            if self.entail.entails(row.sentence, af, ent_seq):
                print(f'Found match: {af} -> {row.sentence} ({row.url})')
                matches.append((af, row.url, row.sentence))
            
            self.nr_checks += 1
            elapsed_s = time.time() - start_s
            if elapsed_s > entailment_s:
                print(f'Timeout during matching')
                break
        
        return matches
    
    def write_stats(self, outfile):
        """ Write statistics to given output file. 
        
        Args:
            outfile: path to output file
        """
        with open(outfile, 'w') as file:
            file.write('nr_facts\tnr_checks\telapsed_s\n')
            elapsed_s = time.time() - self.init_s
            file.write(f'{self.nr_facts}\t{self.nr_checks}\t{elapsed_s}')