'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import checker.util
import gym
import numpy as np
from gym import spaces    

class TreeEnv(gym.Env):
    """ Environment for optimizing detection plans via search tree. """
    
    def __init__(self, detector, nr_episodes, timeout_s, stats_file):
        """ Initializes Web checking environment. 
        
        Args:
            detector: engine processing detector plans
            nr_episodes: at most that many episodes
            timeout_s: timeout per detection in seconds
            stats_file: write statistics to this file
        """
        self.detector = detector
        self.nr_episodes = nr_episodes
        self.timeout_s = timeout_s
        self.stats_file = stats_file
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Discrete(6)
        self.cur_plan = np.zeros(shape=(5,), dtype=np.int64)
        self.matches = []
        self.nr_evals = 0
        self.pid_to_reward = {}
        for p in checker.util.all_plans():
            p_id = checker.util.plan_to_id(p)
            self.pid_to_reward[p_id] = 0
        self.reset()
        
    def best_plan(self):
        """ Determines best plan based on statistics so far. """
        best_p_id = max(self.pid_to_reward, key=self.pid_to_reward.get)
        return checker.util.id_to_plan(best_p_id)
        
    def step(self, action):
        """ Action determines next plan property. 
        
        Args:
            action: binary decision on next property
        """
        if self.nr_evals >= self.nr_episodes:
            return self._observe(), 0, False, {}
            
        if self.decision >= 5:
            reward = self._evaluate()
            print(f'Reward: {reward}; evaluations: {self.nr_evals}')
            done = True
        else:
            self.cur_plan[self.decision] = action
            reward = 0
            done = False
        
        self.decision += 1
            
        return self._observe(), reward, done, {}
        
    def reset(self):
        """ Reset decision index and current plan. """
        self.decision = 0
        for i in range(5):
            self.cur_plan[i] = 0
        return self._observe()
    
    def _evaluate(self):
        """ Evaluates current detector plan and returns reward. 
        
        Returns:
            Reward (higher if more matches were found until timeout)
        """
        print(f'Evaluating plan {self.cur_plan}')
        new_matches = self.detector.execute(self.cur_plan, self.timeout_s)
        self.matches += new_matches        
        reward = len(new_matches)
        
        p_id = checker.util.plan_to_id(self.cur_plan)
        self.pid_to_reward[p_id] += reward
        
        self.nr_evals += 1
        stats = [str(self.nr_evals), str(reward)]
        stats += [str(self.cur_plan[i]) for i in range(5)]
        self.stats_file.write(",".join(stats) + '\n')
        
        return reward
    
    def _observe(self):
        """ Generate observation. """
        return self.decision