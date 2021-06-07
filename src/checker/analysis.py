'''
Created on Jun 6, 2021

@author: immanueltrummer
'''
import numpy as np
import itertools
import re

def count_matches(matches_path):
    """ Count number of matches in file. 
    
    Args:
        matches_path: path to file containing matches
        
    Returns:
        count of matches
    """
    with open(matches_path) as file:
        text = file.read()
        nr_matches = len(re.findall(r'\'\), \(\'', text))+1
        nr_matches += len(re.findall(r'\'\), \("', text))
        nr_matches += len(re.findall(r'"\), \(\'', text))
        nr_matches += len(re.findall(r'"\), \("', text))
        
    return nr_matches

z_o = [0, 1]
plans = [np.array(p) for p in itertools.product(z_o, z_o, z_o, z_o, z_o)]

for p in plans:
    p_id = "_".join([str(s) for s in list(p)])
    count_matches
    file_path = f'/Users/immanueltrummer/Temp/webchecker/original/wc_results/matches_{p_id}'
    nr_matches = count_matches(file_path)
    print(f'{p_id}: {nr_matches}')
    
rl_path = f'/Users/immanueltrummer/Temp/webchecker/original/wc_results/matches_RL'
nr_rl_matches = count_matches(rl_path)
print(f'RL: {nr_rl_matches}')