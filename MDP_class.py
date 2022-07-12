import numpy as np

class MDP:

    # Initilize the size of the tree
    def __init__(self,state_init,check):
        # state_init is the current state and origin of the tree
        # check is the function that determines whether a state-action pair is possible

        # define the set of states
        self.a = 3 # number of intersections (or time instances) to simulate forward
        self.D = 4 # number of directions possible at each intersection
        self.n_state_action_pairs = num_s_a_pairs(self.a)
        T = 1 # assume that we know for certain that an action will move one state to another
        self.state_init = state_init

        self.MDP_tree = np.zeros((self.n_state_action_pairs,self.a))
        self.values = -100*np.ones((self.n_state_action_pairs,self.a))

    # define tree reward function
    def reward(lost_lives, treasures):
      return treasures - (lost_lives*3)

    def node_parent(row,col):
        return int(np.floor(row/self.D)),col-1

    def node_child(row,col,dir):
        return row*self.D+dir,col+1

    def num_s_a_pairs(col):
        return self.D**(col+1)

    def populate_tree():
        for a_i in range(self.a):
            for s_a_pair in range(self.n_state_action_pairs):
                if a_i==0:
                    parent_state = self.state_init
                else:
                    parent_state = self.MDP_tree[self.node_parent(s_a_pair,a_i)]
                if parent_state.possible:
                    action = s_a_pair % self.D # the remainder of s_a_pair/D
                    child_state = state(parent_state.trial_time, parent_state.player, action)
                    if child_state.possible:
                        child_state.simulate()
                        self.MDP_tree[self.node_child(s_a_pair,a_i)] = child_state
