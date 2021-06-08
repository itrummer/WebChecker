'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import argparse
import checker.match
import checker.rl
import itertools
import json
import numpy as np
from stable_baselines3 import A2C
import stable_baselines3.common.evaluation

# Login data can be retrieved at https://programmablesearchengine.google.com/
parser = argparse.ArgumentParser(description='Simple test for WebChecker')
parser.add_argument('key', type=str, help='Specify the Google API key')
parser.add_argument('cse', type=str, help='Specify SE ID')
parser.add_argument('naf_path', type=str, help='Path to number mistakes')
parser.add_argument('eaf_path', type=str, help='Path to entity mistakes')
parser.add_argument('nr_rounds', type=int, help='Number of iterations')
parser.add_argument('timeout_s', type=int, help='Timeout in seconds')
parser.add_argument('mode', type=str, help='Try all plans (a) or use RL (r)')
args = parser.parse_args()
print(args)

retry_af = False

def write_stats(detector, matches, p_id):
    """ Write benchmark results to file. 
    
    Args:
        detector: detector used for matching
        matches: matches found on the Web
        p_id: use as suffix for file names
    """
    stat_file = f'stats_{p_id}'
    detector.write_stats(stat_file)
    match_file = f'matches_{p_id}'
    with open(match_file, 'w') as file:
        file.write(str(matches))
    
    json_res = {}
    json_res['matches'] = []
    for t, u, m in matches:
        json_m = {}
        json_m['triple'] = t
        json_m['url'] = u
        json_m['match'] = m
        json_res['matches'].append(json_m)
    json_path = f'json_matches_{p_id}'
    with open(json_path, 'w') as file:
        json.dump(json_res, file)

if args.mode == 'a':
    
    # Try out all plans for comparison
    print('Trying all plans ...')
    z_o = [0, 1]
    plans = [np.array(p) for p in itertools.product(z_o, z_o, z_o, z_o, z_o)]
    
    for p in plans:
        
        p_id = "_".join([str(s) for s in list(p)])
        detector = checker.match.Detector(
            args.key, args.cse, args.naf_path, args.eaf_path, retry_af)
        matches = []
        
        for i in range(args.nr_rounds):            
            new_matches = detector.execute(p, args.timeout_s)
            print(f'New matches: {new_matches}')
            matches += new_matches
        
        write_stats(detector, matches, p_id)
            
elif args.mode == 'r':
    
    # Use RL to converge to near-optimal plans
    print('Select plans via reinforcement learning ...')
    with open('rl_stats', 'w') as file:
        detector = checker.match.Detector(
            args.key, args.cse, args.naf_path, 
            args.eaf_path, retry_af)
        env = checker.rl.TreeEnv(
            detector, args.nr_rounds, 
            args.timeout_s, file)
        model = A2C(
            'MlpPolicy', env, verbose=True,
            normalize_advantage=True)
        
        learning_steps = (args.nr_rounds / 4) * 6
        eval_episodes = (args.nr_rounds / 4) * 3
        print(f'Learning for {learning_steps} steps ...')
        model.learn(total_timesteps=learning_steps)
        
        best_plan = env.best_plan()
        print(f'Evaluating {best_plan} for {eval_episodes} episodes ...')
        matches = env.matches
        for i in range(eval_episodes):
            matches += detector.execute(best_plan, args.timeout_s)
        
        write_stats(detector, matches, 'RL')
    
else:
    
    print(f'Unknown mode: {args.mode}')