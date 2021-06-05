'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import argparse
import checker.match
import checker.rl
import itertools
import numpy as np
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import A2C

# Login data can be retrieved at https://programmablesearchengine.google.com/
parser = argparse.ArgumentParser(description='Simple test for WebChecker')
parser.add_argument('key', type=str, help='Specify the Google API key')
parser.add_argument('cse', type=str, help='Specify SE ID')
parser.add_argument('nr_rounds', type=int, help='Number of iterations')
parser.add_argument('timeout_s', type=int, help='Timeout in seconds')
args = parser.parse_args()
print(args)

# Try out baselines
z_o = [0, 1]
plans = [np.array(p) for p in itertools.product(z_o, z_o, z_o, z_o)]

for p in plans:
    
    p_id = "_".join([str(s) for s in list(p)])
    detector = checker.match.Detector(args.key, args.cse)
    matches = []
    
    for i in range(args.nr_rounds):
        
        new_matches = detector.execute(p, args.timeout_s)
        print(f'New matches: {new_matches}')
        matches += new_matches

    stat_file = f'stats_{p_id}'
    detector.write_stats(stat_file)
    match_file = f'matches_{p_id}'
    with open(match_file, 'w') as file:
        file.write(matches)

# Run reinforcement learning
# detector = checker.match.Detector(args.key, args.cse)
# env = checker.rl.CheckingEnv(detector)
# check_env(env)
# model = A2C('MlpPolicy', env, verbose=True, 
            # normalize_advantage=True).learn(total_timesteps=100)
            #
# print(f'Matches: {env.matches}')