'''
Created on Jun 8, 2021

@author: immanueltrummer
'''
import itertools
import numpy as np

def plan_to_id(plan):
    """ Transform plan to string ID. 
    
    Args:
        plan: plan represented as numpy array
        
    Returns:
        plan represented as string
    """
    nr_props = plan.shape[0]
    properties = [str(plan[i]) for i in range(nr_props)]
    return ''.join(properties)

def id_to_plan(plan_id):
    """ Transform string ID to plan. 
    
    Args:
        plan_id: string representation of plan
        
    Returns:
        plan represented as numpy array
    """
    nr_props = len(plan_id)
    plan = np.zeros(nr_props, dtype=np.int64)
    for i in range(nr_props):
        plan[i] = int(plan_id[i])
    
    return plan

def all_plans():
    """ Generates all plans (assuming five binary properties). """
    z_o = [0, 1]
    return [np.array(p) for p in itertools.product(z_o, z_o, z_o, z_o, z_o)]