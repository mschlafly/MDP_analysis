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
        self.values = np.zeros((self.n_state_action_pairs,self.a))
        self.N_sim = np.zeros((self.n_state_action_pairs,self.a))

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
        num_proc = 14

        # create array for storing action/reward pairs
        sim_result = np.zeros((3,self.a))
        sim_result_len = sim_result.reshape(-1).shape[0]

        # Set up different processes to for each simulation in loop
        sample = 0
        samples_left = num_sims-sample
        if num_sims>=num_proc:
            samples_left = num_sims-sample
            while samples_left>=num_proc:
                # print(str(samples_left)+' samples left')
                processes = []
                shared_array = []
                success_arr = Array('d', range(num_proc))
                # timeout = time.time() + num_proc*cpu_timeout/num_sims
                for i in range(num_proc):
                    success_arr[i] = 0
                    shared_array.append(Array('d', range(sim_result_len)))
                    # action_sim = random.sample([0,1,2,3],2)
                    # print(action_sim)
                    processes.append(Process(target=self.simulate, args=(shared_array[i],success_arr,i)))
                    sample = sample + 1
                for i in range(num_proc):
                    processes[i].start()
                for i in range(num_proc):
                    processes[i].join()
                for i in range(num_proc):
                    # print('success_arr',i,success_arr[i])
                    if success_arr[i]==1:
                        # print('shared_array',shared_array[i][:])
                        self.update_tree_with_sim(shared_array[i][:])
                    if processes[i].is_alive():
                        print(0,i,'process is still alive')
                samples_left = num_sims-sample
        # compute the remaining samples
        processes = []
        shared_array = []
        success_arr = Array('d', range(samples_left))
        # timeout = time.time() + samples_left*cpu_timeout/num_sims
        for i in range(samples_left):
            success_arr[i] = 0
            shared_array.append(Array('d', range(sim_result_len)))
            processes.append(Process(target=self.simulate, args=(shared_array[i],success_arr,i)))
            sample = sample + 1
        for i in range(samples_left):
            processes[i].start()
        for i in range(samples_left):
            processes[i].join()
        for i in range(samples_left):
            if success_arr[i]==1:
                self.update_tree_with_sim(shared_array[i][:])
        return True

    def simulate(self,shared_array=0,success_arr=0,i=-1):
        sim_result = np.zeros((3,self.a))
        include_treasure = True

        for a_i in range(self.a):
            action = random.choice([0,1,2,3])
            if a_i==0:
                system_state = copy.deepcopy(self.state_init)
                dist_to_treasure_prev = np.sqrt(((system_state.treasure.x - system_state.player.x)**2) + ((system_state.treasure.y - system_state.player.y)**2))
                include_treasure = system_state.include_treasure
            elif a_i==1:
                for adv in system_state.adversaries:
                    adv.caught_player = 0
                sim_result[1,a_i] = 0
            lost_lives, dist_to_treasure, found_treasure = system_state.simulate(action)

            # Update reward and N
            if include_treasure:
                r = self.reward(lost_lives, dist_to_treasure, dist_to_treasure_prev)
            else:
                # If the treasure has already been found, do not include it in the reward
                r = self.reward(lost_lives, dist_to_treasure, dist_to_treasure)
            sim_result[0,a_i] = action
            sim_result[1,a_i] = r
            sim_result[2,a_i] = 1

            if found_treasure:
                include_treasure = False

        sim_result_raveled = sim_result.reshape(-1)
        if i!=-1:
            for ii in range(sim_result_raveled.shape[0]):
                shared_array[ii] = sim_result_raveled[ii]
            success_arr[i] = 1
        else:
            return sim_result_raveled

    def update_tree_with_sim(self,sim_output):
        result = np.array(sim_output).reshape((3,self.a))
        for a_i in range(self.a):
            action = result[0,a_i]
            if a_i==0:
                # set position of the first child state
                row = int(action); col = 0
            else:
                # Get the grid position of the next state
                row,col = self.node_child(row,col,action)
            if result[2,a_i]==1:
                self.values[row,col] += result[1,a_i]
                self.N_sim[row,col] += 1

    def populate_tree(self,num_sims):
        for sim in range(num_sims):

            sim_result_raveled = self.simulate()
            self.update_tree_with_sim(sim_result_raveled)
            # # t_start = time.time()
            # # print('\n new sim',t_start)
            # for a_i in range(self.a):
            #     action = choice([0,1,2,3])
            #     if a_i==0:
            #         system_state = copy.deepcopy(self.state_init)
            #         dist_to_treasure_prev = copy.deepcopy(system_state.dist_to_treasure)
            #         # set position of the first child state
            #         row = action; col = 0
            #     else:
            #         # Get the grid position of the next state
            #         row,col = self.node_child(row,col,action)
            #     # system_state.action = action
            #     # prev_player_position = copy.deepcopy(system_state.player)
            #     lost_lives, dist_to_treasure = system_state.simulate(action)
            #
            #     # Update reward and N
            #     if system_state.include_treasure:
            #         r = self.reward(lost_lives, dist_to_treasure, dist_to_treasure_prev)
            #     else:
            #         # If the treasure has already been found, do not include it in the reward
            #         r = self.reward(lost_lives, dist_to_treasure, dist_to_treasure)
            #     dist_to_treasure_prev = dist_to_treasure
            #     # if self.reward(lost_lives, treasures)>1:
            #     # print('value', lost_lives, treasures)
            #     self.N_sim[row,col] += 1
            # print(time.time()-t_start)s

    # update the values on the tree according to the Bellman equation
    def update_value_tree(self):
        # Loop through tree, averaging across simulations
        count_unreached = 0
        count_reached = 0
        for a_i in range(self.a):
            for i in range(self.num_s_a_pairs(a_i)):
                if self.N_sim[i,a_i]>0:
                    self.values[i,a_i] = np.divide(self.values[i,a_i],self.N_sim[i,a_i])
                    count_reached += 1
                else:
                    self.values[i,a_i] = -50
                    count_unreached += 1

                # # Try not including adversaries you meet in the next turn
                # if a_i==0:
                #     self.values[i,a_i] = 0

        if count_unreached/(count_reached+count_unreached)>.01:
            print('\n\n\n MAY NOT HAVE ENOUGH SIMULATIONS')
            print(count_unreached/(count_reached+count_unreached))
        # if sum(self.values[:4,0])>0.01:
        #     # print(self.values[:4,0])
        #     return False

        # Loop backwards through tree
        for a_i in range(self.a-2,-1,-1):
            for i in range(self.num_s_a_pairs(a_i)):
                # Take the maximum of the values of the child nodes
                row,col = self.node_child(i,a_i,0)
                values = self.values[row:row+self.D,col]
                shuffle(values) # to prevent bias
                self.values[i,a_i] = np.amax(values)
                # self.values[i,a_i] = np.mean(values)
        return True
