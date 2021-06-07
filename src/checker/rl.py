'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import gym
import numpy as np
from gym import spaces

class CheckingEnv(gym.Env):
    """ Environment for optimizing plans for Web checking. """
    
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
        self.action_space = spaces.MultiDiscrete([5, 2])
        self.observation_space = spaces.MultiBinary(4)
        self.cur_plan = np.zeros(shape=(4,), dtype=np.int64)
        self.matches = []
        self.nr_evals = 0
        
    def step(self, action):
        """ Change detector plan or search matches. 
        
        Args:
            action: plan property to change and new value
        """
        if self.nr_evals >= self.nr_episodes:
            return self.cur_plan, 0, False, {}
            
        print(action)
        prop, value = action
        if prop < 4:
            self.cur_plan[prop] = value
            reward = 0
            done = False
        else:
            reward = self._evaluate()
            done = True
            
        return self.cur_plan, reward, done, {}
        
    def reset(self):
        """ Reset current plan. """
        for i in range(4):
            self.cur_plan[i] = 0
        return self.cur_plan
    
    def _evaluate(self):
        """ Evaluates current detector plan and returns reward. 
        
        Returns:
            Reward (higher if more matches were found until timeout)
        """
        print(f'Evaluating plan {self.cur_plan}')
        prior_nr_checks = self.detector.nr_checks
        full_plan = np.zeros(shape=(5,), dtype=np.int64)
        for i in range(4):
            full_plan[i+1] = self.cur_plan[i]
        new_matches = self.detector.execute(full_plan, self.timeout_s)
        
        self.matches += new_matches
        new_checks = self.detector.nr_checks - prior_nr_checks        
        reward = len(new_matches) + 0.01 * new_checks
        self.nr_evals += 1
        
        self.stats_file.write(
            f'{self.nr_evals},{reward},{self.cur_plan[0]},' \
            f'{self.cur_plan[1]},{self.cur_plan[2]},{self.cur_plan[3]}\n')
        
        return reward
    

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
        self.observation_space = spaces.Discrete(5)
        self.cur_plan = np.zeros(shape=(5,), dtype=np.int64)
        self.matches = []
        self.nr_evals = 0
        self.reset()
        
    def step(self, action):
        """ Action determines next plan property. 
        
        Args:
            action: binary decision on next property
        """
        if self.nr_evals >= self.nr_episodes:
            return self.cur_plan, 0, False, {}
            
        if self.decision >= 5:
            reward = self._evaluate()
            done = True
        else:
            self.cur_plan[self.decision] = action
            reward = 0
            done = False
        
        self.decision += 1
            
        return self.decision, reward, done, {}
        
    def reset(self):
        """ Reset decision index and current plan. """
        self.decision = 1
        for i in range(5):
            self.cur_plan[i] = 0
        return self.decision
    
    def _evaluate(self):
        """ Evaluates current detector plan and returns reward. 
        
        Returns:
            Reward (higher if more matches were found until timeout)
        """
        print(f'Evaluating plan {self.cur_plan}')
        prior_nr_checks = self.detector.nr_checks
        new_matches = self.detector.execute(self.cur_plan, self.timeout_s)
        
        self.matches += new_matches
        new_checks = self.detector.nr_checks - prior_nr_checks        
        reward = len(new_matches) + 0.01 * new_checks
        self.nr_evals += 1
        
        stats = [str(self.nr_evals), str(reward)]
        stats += [self.cur_plan[i] for i in range(5)]
        self.stats_file.write(",".join(stats) + '\n')
        
        return reward