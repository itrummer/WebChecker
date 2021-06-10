'''
Created on Jun 6, 2021

@author: immanueltrummer
'''
import itertools
import numpy as np
import pandas as pd
import os
import plotly.express as px
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

p_counts = []
for p in plans:
    p_id = "_".join([str(s) for s in list(p)])
    count_matches
    file_path = f'/Users/immanueltrummer/Temp/webchecker/original/wc_results/matches_{p_id}'
    nr_matches = count_matches(file_path)
    print(f'{p_id}: {nr_matches}')
    p_counts.append([p_id, nr_matches])
    
rl_path = f'/Users/immanueltrummer/Temp/webchecker/original/wc_results/matches_RL'
nr_rl_matches = count_matches(rl_path)
print(f'RL: {nr_rl_matches}')

os.environ['PATH'] = os.environ.get('PATH') + \
    ':/opt/homebrew/anaconda3/envs/literate/bin' + \
    ':/opt/homebrew/bin'
df = pd.DataFrame(p_counts, columns=['plan', 'matches'])
fig = px.bar(df, x='plan', y='matches')
fig.update_layout(
    font_family='Serif', font_size=11, 
    xaxis_title='Plan', yaxis_title='Nr. Matches',
    margin_l=5, margin_r=5, margin_t=5, margin_b=5)
fig.write_image('nr_matches.eps', width='600', height='200', scale=1)
fig.show()