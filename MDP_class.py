import numpy as np
from numpy.random import choice, shuffle
from state import state
import copy

class MDP:

    # Initilize the size of the tree
    def __init__(self,state_init):
        # state_init is the current state and origin of the tree
        # check is the function that determines whether a state-action pair is possible

        # define the set of states
        self.a = 4 # number of intersections (or time instances) to simulate forward
        self.D = 4 # number of directions possible at each intersection
        self.n_state_action_pairs = self.num_s_a_pairs(self.a-1)
        T = 1 # assume that we know for certain that an action will move one state to another
        self.state_init = state_init

        # self.MDP_tree = np.zeros((self.n_state_action_pairs,self.a))
        self.values = -100*np.ones((self.n_state_action_pairs,self.a))
        self.N_sim = np.zeros((self.n_state_action_pairs,self.a))

    # define tree reward function
    # def reward(self, lost_lives, treasures):
    def reward(self, lost_lives, dist_to_treasure, dist_to_treasure_prev):
      return - (lost_lives*3) + (dist_to_treasure_prev - dist_to_treasure)/25

    def node_parent(self,row,col):
        return int(np.floor(row/self.D)),col-1

    def node_child(self,row,col,dir):
        return row*self.D+dir,col+1

    def num_s_a_pairs(self,col):
        return self.D**(col+1)

    def populate_tree(self,num_sims):
        for sim in range(num_sims):
            # print('\n new sim')
            for a_i in range(self.a):
                action = choice([0,1,2,3])
                if a_i==0:
                    system_state = copy.deepcopy(self.state_init)
                    dist_to_treasure_prev = copy.deepcopy(system_state.dist_to_treasure)
                    # set position of the first child state
                    row = action; col = 0
                else:
                    # Get the grid position of the next state
                    row,col = self.node_child(row,col,action)
                system_state.action = action
                # prev_player_position = copy.deepcopy(system_state.player)
                lost_lives, dist_to_treasure = system_state.simulate()
                # If the treasure has already been found, do not include it in the reward
                if not system_state.include_treasure:
                    dist_to_treasure_prev = dist_to_treasure

                # print('adv0 new pos',system_state.adversaries[0].pos.x,system_state.adversaries[0].pos.y)
                # Update reward and N
                self.values[row,col] = self.reward(lost_lives, dist_to_treasure, dist_to_treasure_prev)
                dist_to_treasure_prev = dist_to_treasure
                # if self.reward(lost_lives, treasures)>1:
                # print('value', lost_lives, treasures)
                self.N_sim[row,col] += 1

    # update the values on the tree according to the Bellman equation
    def update_value_tree(self):
        # Take the expectation of each node
        self.values = np.divide(self.values, self.N_sim)

        # Loop backwards through tree
        for a_i in range(self.a-2,-1,-1):
            for i in range(self.num_s_a_pairs(a_i)):

                # Take the maximum of the values of the child nodes
                row,col = self.node_child(i,a_i,0)
                values = self.values[row:row+self.D,col]
                shuffle(values) # to prevent bias
                self.values[i,a_i] = np.amax(values)

    # def populate_tree_systematically():
    #     for a_i in range(self.a):
    #         for s_a_pair in range(self.n_state_action_pairs):
    #             if a_i==0:
    #                 parent_state = self.state_init
    #             else:
    #                 parent_state = self.MDP_tree[self.node_parent(s_a_pair,a_i)]
    #             if parent_state.possible:
    #                 action = s_a_pair % self.D # the remainder of s_a_pair/D
    #                 child_state = state(parent_state.trial_time, parent_state.player, action)
    #                 if child_state.possible:
    #                     child_state.simulate()
    #                     self.MDP_tree[self.node_child(s_a_pair,a_i)] = child_state
