'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import collections
import pandas as pd

class Access:
    """ Provides access to AKB entries. """
    
    def __init__(self, akb_path):
        """ Initialize access to AKB.
         
         Args:
            akb_path: path to AKB
        """
        self.akb = pd.read_csv(akb_path, sep='\t')
        self.nr_afs = self.akb.shape[0]
        self.id_to_ctr = collections.defaultdict(lambda:-1)
        
        print(f'Read AKB from {akb_path} - sample:')
        print(self.akb.sample())
        print(f'Number of entries: {self.nr_afs}')
        
    def _get_triple(self, triple_idx):
        """ Returns triple with given index. 
        
        Args:
            triple_idx: number of triple to return
            
        Returns:
            subject, predicate, object
        """
        subj = self.akb.loc[triple_idx, 'subj']
        pred = self.akb.loc[triple_idx, 'pred']
        obj = self.akb.loc[triple_idx, 'obj']
        return subj, pred, obj

    def _is_relevant(self, triple_idx, pred):
        """ Returns true iff referenced triple passes filter. 
        
        Args:
            triple_idx: check triple at this index
            pred: check using this filter condition
            
        Returns:
            true iff the triple passes the filter
        """
        if pred == 0:
            return True
        else:
            _, _, obj = self._get_triple(triple_idx)
            return True if len(obj) > 10 else False
        
    def next_triple(self, req_id, pred):
        """ Returns next triple for specific requester.
        
        Args:
            req_id: requester ID (a list)
            pred: type of triple filter
            
        Returns:
            next triple for specific requester
        """
        req_int_id = sum([2**i * req_id[i] for i in range(req_id.shape[0])])
        cur_idx = self.id_to_ctr[req_int_id] + 1
        while cur_idx < self.nr_afs and not self._is_relevant(cur_idx, pred):
            cur_idx += 1
        
        if cur_idx >= self.nr_afs:
            cur_idx = 0
        self.id_to_ctr[req_int_id] = cur_idx
        
        return self._get_triple(cur_idx)