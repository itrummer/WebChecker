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
import plotly.graph_objects as go

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
    
    p_label_parts = []
    # Number versus entity mistakes
    p_akb = 'N' if p[0] == 0 else 'E'
    # All versus only long triples
    p_apred = 'A' if p[1] == 0 else 'L'
    # Non-quoted versus quoted Web queries
    p_query = 'N' if p[2] == 0 else 'Q'
    # All versus only short Web sites
    p_wpred = 'A' if p[3] == 0 else 'S'
    # First check is high or low precision
    p_ent = 'H' if p[4] == 0 else 'L'
    p_label = p_akb + p_apred + p_query + p_wpred + p_ent
    p_counts.append([p_label, nr_matches])
    
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
    margin_l=5, margin_r=5, margin_t=5, margin_b=5,
    xaxis=go.layout.XAxis(tickangle=-45))
fig.add_hline(y=112, line=dict(color='red', width=5))
fig.add_hline(y=104, line=dict(color='red', width=2, dash='dash'))
fig.add_hline(y=118, line=dict(color='red', width=2, dash='dash'))
fig.write_image('nr_matches.eps', width='600', height='250', scale=1)
fig.show()