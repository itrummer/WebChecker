'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import gym
import checker.nlp
import numpy as np
import time
from gym import spaces

class CheckingEnv(gym.Env):
    """ Environment for optimizing plans for Web checking. """
    
    def __init__(self, akbs, web):
        """ Initializes Web checking environment. 
        
        Args:
            akbs: list of anti-knowledge bases (currently: two!) 
            web: wrapper for issuing Google search queries
        """
        self.akbs = akbs
        self.web = web
        self.entail = checker.nlp.EntailmentUtil()
        self.action_space = spaces.MultiBinary([6, 2])
        self.observation_space = spaces.MultiBinary(5)
        self.cur_plan = np.zeros(shape=(5,), dtype=np.int64)
        self.matches = []
        
    def step(self, action):
        """ Change detection plan or search matches. 
        
        Args:
            action: plan property to change and new value
        """
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
        """ Evaluates current detection plan and returns reward. 
        
        Returns:
            Reward (higher if more matches were found until timeout)
        """
        akb_idx = self.cur_plan[0]
        akb_filter = self.cur_plan[1]
        web_idx = self.cur_plan[2]
        web_filter = self.cur_plan[3]
        ent_seq = self.cur_plan[4]
        
        req_id = self.cur_plan[1:]
        akb = self.akbs[akb_idx]
        triple = akb.next_triple(req_id, akb_filter)
        web_result = self.web.match_triple(triple, web_idx, web_filter)
        
        reward = 0
        start_s = time.time()
        for l in web_result.loc[:, 'sentence']:            
            af = triple[0] + ' ' + triple[1] + ' ' +triple[2]
            if self.entail.entails(l, af, ent_seq):
                self.matches.append((af, l))
                reward += 1
                
            elapsed_s = time.time() - start_s
            if elapsed_s > 30:
                break
            
        return reward