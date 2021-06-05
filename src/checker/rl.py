'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import gym
import numpy as np
from gym import spaces

class CheckingEnv(gym.Env):
    """ Environment for optimizing plans for Web checking. """
    
    def __init__(self, detector, timeout_s):
        """ Initializes Web checking environment. 
        
        Args:
            detector: engine processing detector plans
            timeout_s: timeout per detection in seconds
        """
        self.detector = detector
        self.timeout_s = timeout_s
        self.action_space = spaces.MultiDiscrete([6, 2])
        self.observation_space = spaces.MultiBinary(5)
        self.cur_plan = np.zeros(shape=(5,), dtype=np.int64)
        self.matches = []
        
    def step(self, action):
        """ Change detector plan or search matches. 
        
        Args:
            action: plan property to change and new value
        """
        print(action)
        prop, value = action
        if prop < 5:
            self.cur_plan[prop] = value
            reward = 0
            done = False
        else:
            reward = self._evaluate()
            done = True
            
        return self.cur_plan, reward, done, {}
        
    def reset(self):
        """ Reset current plan. """
        for i in range(5):
            self.cur_plan[i] = 0
        return self.cur_plan
    
    def _evaluate(self):
        """ Evaluates current detector plan and returns reward. 
        
        Returns:
            Reward (higher if more matches were found until timeout)
        """
        print(f'Evaluating plan {self.cur_plan}')
        new_matches = self.detector.execute(self.cur_plan, self.timeout_s)
        self.matches += new_matches
        return len(new_matches)