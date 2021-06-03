'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
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
        self.cur_idx = 0
        
        print(f'Read AKB from {akb_path} - sample:')
        print(self.akb.sample())
        print(f'Number of entries: {self.nr_afs}')
        
    def next_triple(self):
        """ Returns next triple.
        
        """
        subj = self.akb.loc[self.cur_idx, 'subj']
        pred = self.akb.loc[self.cur_idx, 'pred']
        obj = self.akb.loc[self.cur_idx, 'obj']
        
        self.cur_idx += 1
        if self.cur_idx >= self.nr_afs:
            self.cur_idx = 0
        
        return subj, pred, obj