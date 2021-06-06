'''
Created on Jun 6, 2021

@author: immanueltrummer
'''
import numpy as np
import itertools
import re

z_o = [0, 1]
plans = [np.array(p) for p in itertools.product(z_o, z_o, z_o, z_o, z_o)]

for p in plans:
    p_id = "_".join([str(s) for s in list(p)])
    file = open(f'/Users/immanueltrummer/Temp/webchecker/matches_{p_id}')
    text = file.read()
    nr_triples = len(re.findall(r'\'\), \(\'', text))+1
    print(f'{p_id}: {nr_triples}')