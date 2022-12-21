import numpy as np
from numpy.random import shuffle #choice, choices,
import random
from state import state
import copy
import multiprocessing as mp
from multiprocessing import Process, Queue, Array
import time

class MDP:

    # Initilize the size of the tree
    def __init__(self,state_init,num_actions,MDP_reward_model):
        # state_init is the current state and origin of the tree
        # check is the function that determines whether a state-action pair is possible

        # define the set of states
        self.a = num_actions # number of intersections (or time instances) to simulate forward
        self.D = 4 # number of directions possible at each intersection
        self.n_state_action_pairs = self.num_s_a_pairs(self.a-1)
        T = 1 # assume that we know for certain that an action will move one state to another
        self.state_init = state_init

        # self.MDP_tree = np.zeros((self.n_state_action_pairs,self.a))
        # self.values = np.zeros((self.n_state_action_pairs,self.a))
        self.values = np.zeros(self.n_state_action_pairs)
        # self.N_sim = np.zeros((self.n_state_action_pairs,self.a))
        self.N_sim = np.zeros(self.n_state_action_pairs)

        self.MDP_reward_model = MDP_reward_model

    # define tree reward function
    def reward(self, lost_lives, dist_to_treasure, dist_to_treasure_prev):
      return - (lost_lives*3) + (dist_to_treasure_prev - dist_to_treasure)/25
      # return (dist_to_treasure_prev - dist_to_treasure)/25

    def node_parent(self,row,col):
        return int(np.floor(row/self.D)),col-1

    def node_child(self,row,col,dir):
        return int(row*self.D+dir),col+1

    def num_s_a_pairs(self,col):
        return self.D**(col+1)

    def populate_tree_parallelized(self,num_sims):
        num_proc = 20

        # create array for storing actions
        sim_action_selected = np.zeros(self.a)
        sim_action_selected_len = sim_action_selected.shape[0]

        # Set up different processes to for each simulation in loop
        sample = 0
        samples_left = num_sims-sample
        if num_sims>=num_proc:
            samples_left = num_sims-sample
            while samples_left>=num_proc:
                # print(str(samples_left)+' samples left')
                processes = []
                shared_array = []
                reward_arr = Array('d', range(num_proc))
                success_arr = Array('d', range(num_proc))
                for i in range(num_proc):
                    success_arr[i] = 0
                    shared_array.append(Array('d', range(sim_action_selected_len)))
                    processes.append(Process(target=self.simulate, args=(shared_array[i],reward_arr,success_arr,i)))
                    sample = sample + 1
                for i in range(num_proc):
                    processes[i].start()
                for i in range(num_proc):
                    processes[i].join()
                for i in range(num_proc):
                    if success_arr[i]==1:
                        self.update_tree_with_sim(shared_array[i][:],reward_arr[i])
                    if processes[i].is_alive():
                        print(0,i,'process is still alive')
                samples_left = num_sims-sample
        # compute the remaining samples
        processes = []
        shared_array = []
        reward_arr = Array('d', range(num_proc))
        success_arr = Array('d', range(samples_left))
        for i in range(samples_left):
            success_arr[i] = 0
            shared_array.append(Array('d', range(sim_action_selected_len)))
            processes.append(Process(target=self.simulate, args=(shared_array[i],reward_arr,success_arr,i)))
            sample = sample + 1
        for i in range(samples_left):
            processes[i].start()
        for i in range(samples_left):
            processes[i].join()
        for i in range(samples_left):
            if success_arr[i]==1:
                self.update_tree_with_sim(shared_array[i][:],reward_arr[i])
        return True

    def simulate(self,action_array=0,reward=0,success_arr=0,i=-1):
        action_list = np.zeros(self.a)
        # include_treasure = False

        for a_i in range(self.a):
            action = random.choice([0,1,2,3])
            action_list[a_i] = action
            if a_i==0:
                system_state = copy.deepcopy(self.state_init)
                if system_state.include_treasure:
                    include_treasure = True
                else:
                    include_treasure = False
                dist_to_treasure_prev = np.sqrt(((system_state.treasure.x - system_state.player.x)**2) + ((system_state.treasure.y - system_state.player.y)**2))
                lost_lives, dist_to_treasure = system_state.simulate(action,firstsim=True)
            else:
                lost_lives, dist_to_treasure = system_state.simulate(action,firstsim=False)

        # Update reward and N
        if include_treasure:
            if system_state.include_treasure:
                r = self.reward(lost_lives, dist_to_treasure, dist_to_treasure_prev)
            else:
                # If the treasure has already been found, make sure the reward value is one!
                r = self.reward(lost_lives, dist_to_treasure_prev, dist_to_treasure_prev+25)
        else:
            r = self.reward(lost_lives, dist_to_treasure_prev, dist_to_treasure_prev)

        if i!=-1:
            for ii in range(action_list.shape[0]):
                action_array[ii] = action_list[ii]
            reward[i] = r
            success_arr[i] = 1
        else:
            return action_list, r

    def update_tree_with_sim(self,sim_output,reward):
        # print(sim_output,'should be 6 item array')
        # print(reward,'should a number for reward')
        for a_i in range(self.a):
            action = sim_output[a_i]
            if a_i==0:
                # set position of the first child state
                row = int(action); col = 0
            else:
                # Get the grid position of the next state
                row,col = self.node_child(row,col,action)
        self.values[row] += reward
        self.N_sim[row] += 1
        # print(self.values[col])

    # def populate_tree(self,num_sims):
    #     for sim in range(num_sims):
    #         sim_action_selected_raveled = self.simulate()
    #         self.update_tree_with_sim(sim_action_selected_raveled)

    # update the values on the tree according to the Bellman equation
    def update_value_tree(self):
        # Loop through tree, averaging across simulations
        # print('last iter',self.values.shape,self.values)
        # print('last iter',self.N_sim.shape,self.N_sim)
        count_unreached = 0
        count_reached = 0
        a_i = self.a - 1
        for i in range(self.num_s_a_pairs(a_i)):
            if self.N_sim[i]>0:
                self.values[i] = np.divide(self.values[i],self.N_sim[i])
                count_reached += 1
            else:
                self.values[i] = -50
                count_unreached += 1
        # print(count_reached,count_unreached)

        # Loop backwards through tree
        # print(self.a-2,self.values.shape,self.values)
        # print(self.a-1)
        for a_i in range(self.a-2,-1,-1):
            if a_i == self.a-2:
                values_child = self.values
            else:
                values_child = values_parent
            values_parent = np.zeros(self.num_s_a_pairs(a_i))
            for i in range(self.num_s_a_pairs(a_i)):
                row,col = self.node_child(i,a_i,0)
                values = values_child[row:row+self.D]
                # print(row,col,values,values_new_list)
                if self.MDP_reward_model=='max':
                    values_parent[i] = np.amax(values)
                    # if values_parent[i]<0:
                    #     print('\n\n',values,values_parent[i])
                elif self.MDP_reward_model=='mean':
                    values_new_list = []
                    for val in values:
                        if val!=-50:
                            values_new_list.append(val)
                    if len(values_new_list)!=0:
                        values_parent[i] = np.mean(values_new_list)
                    else:
                        values_parent[i] = -50
            # print(a_i,values_parent.shape,values_parent)
            # print(a_i)
        # print(values_parent,'make sure it is a list of 4 items')
        # if np.amin(values_parent)<-40:
        #     print('Error here')
        #     asidhoih
        return values_parent
