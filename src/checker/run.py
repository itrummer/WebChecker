'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import argparse
import checker.match
import checker.rl
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import A2C

# Login data can be retrieved at https://programmablesearchengine.google.com/
parser = argparse.ArgumentParser(description='Simple test for WebChecker')
parser.add_argument('key', type=str, help='Specify the Google API key')
parser.add_argument('cse', type=str, help='Specify SE ID')
args = parser.parse_args()
print(args)

detector = checker.match.Detector(args.key, args.cse)
env = checker.rl.CheckingEnv(detector)
check_env(env)
model = A2C('MlpPolicy', env, verbose=True, 
            normalize_advantage=True).learn(total_timesteps=100)

print(f'Matches: {env.matches}')