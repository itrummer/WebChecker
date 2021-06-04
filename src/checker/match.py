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
    
    def __init__(self, api_key, cse):
        """ Initialize AKB and web access entailment checks.
        
        Args:
            api_key: API key for Google customized search engine
            cse: Google custom search engine ID
        """
        self.web = checker.web.Access(api_key, cse)
        akb_number = checker.akb.Access('/Users/immanueltrummer/Papers/WebChecker/akb_numbers.tsv')
        akb_entity = checker.akb.Access('/Users/immanueltrummer/Papers/WebChecker/akb_entities.tsv')
        self.akbs = [akb_number, akb_entity]
        self.entail = checker.nlp.EntailmentUtil()
        
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
        
        req_id = plan[1:]
        akb = self.akbs[akb_idx]
        triple = akb.next_triple(req_id, akb_filter)
        web_result = self.web.match_triple(triple, web_idx, web_filter)

        matches = []        
        start_s = time.time()
        for l in web_result.loc[:, 'sentence']:            
            af = triple[0] + ' ' + triple[1] + ' ' +triple[2]
            if self.entail.entails(l, af, ent_seq):
                print(f'Found match: {af} -> {l}')
                self.matches.append((af, l))
                
            elapsed_s = time.time() - start_s
            if elapsed_s > timeout_s:
                break
        
        return matches