from read_data import trial_data
from main_utils import *
from env_utils import environment
from plot_MDP import plot_MDP_in_environment
from env_utils import position, environment
from state import adversary_state
from state import state
import copy
import matplotlib.pyplot as plt
import csv
import numpy as np
import time

###############################################################################
# Parameters
###############################################################################

num_actions = 6
num_sims = 30000
include_treasure = True
MDP_reward_model = 'mean'

environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

###############################################################################
# Main script
###############################################################################
player = position(6,22)
player_action = 0
adv_list = []

# Treasure
treasure = position(20,3)

trial_time = 0
env = 1
environ = environment('high')
current_state = state(trial_time,player_action,player,adv_list,treasure,environ)

# [game_time, agent_id, probability_observed, pos_x, pos_y, action, chasing_bool, ignore]
# observations = [[0,0,.5,11,26,3,False,True],
# observations = [[0,1,.5,3,4,0,False,True],
#                 [0,2,.5,10,7,3,False,True]]
# observations = [[0,0,.5,11,26,3,False,True],
#                 # [0,1,.5,14,4,0,False,True],
#                 [0,1,.5,16,4,0,False,True],
#                 # [0,1,.5,3,8,0,False,True],
#                 [0,2,.5,14,3,3,False,True],
#                 [0,3,.5,5,16,1,False,True]]
                # [0,2,.5,15,7,3,False,True]]
# Can't see any adversaries
observations = [[0,0,.5,11,26,3,False,True],
                [0,2,.5,9,16,3,False,True],
                [0,1,.5,12,11,0,False,True]]
# Sees one of the adversaries
observations = [[0,0,1,6,26,3,False,True],
                # [0,2,.5,9,16,3,False,True],
                # [0,2,.5,4,16,1,False,True],
                [0,2,.5,9,16,3,False,True],
                [0,1,.5,12,11,0,False,True],
                [0,3,.5,12,18,2,False,True]]
                # [0,3,.5,3,18,2,False,True]]
observations = [[0,0,1,6,26,3,False,True]]

# clear state knowledge of adversary locations
current_state.adversaries = []
current_state.partially_observable = True

current_state.update_state_with_observations(observations)
# print(len(current_state.adversaries))

next_action_reward, MDP_i = run_MDP(current_state,num_sims,num_actions,MDP_reward_model)
print('Action Costs: '+str(next_action_reward))
plot_MDP_in_environment(MDP_i,  100)

# best path
action_list = []
best_action_dir = np.argmax(next_action_reward)
action_list.append(best_action_dir)
row=0
col=0
for i in range(1,6):
    row,col = MDP_i.node_child(row+best_action_dir,col,0)
    next_action_reward = MDP_i.values[row:(row+4),col]
    best_action_dir = np.argmax(next_action_reward)
    print('Action Costs '+str(i)+' :'+str(next_action_reward))
    action_list.append(best_action_dir)
print(action_list)
plot_MDP_in_environment(MDP_i,  1, action_list = action_list)
plt.savefig('best_path.png')
plt.savefig('best_path.pdf')

# plot_MDP_in_environment(MDP_i,  1, action_list = [0,1,1,1,1,1])
# plt.savefig('1.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [0,1,1,1,2,1])
# plt.savefig('2.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [0,3,2,2,3,2])
# plt.savefig('3.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [0,3,0,2,2,2])
# plt.savefig('4.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [1,0,1,1,1,1])
# plt.savefig('5.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [1,1,1,1,2,2])
# plt.savefig('6.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [1,2,2,3,3,2])
# plt.savefig('7.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [1,1,1,2,2,2])
# plt.savefig('8.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [2,2,1,2,1,2])
# plt.savefig('9.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [2,1,1,1,1,2])
# plt.savefig('10.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [2,2,2,2,1,1])
# plt.savefig('11.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [2,3,2,2,2,1])
# plt.savefig('12.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [3,0,1,1,1,0])
# plt.savefig('13.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [3,3,2,2,2,2])
# plt.savefig('14.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [3,2,2,1,2,2])
# plt.savefig('15.png')
# plot_MDP_in_environment(MDP_i,  1, action_list = [3,2,2,2,2,1])
# plt.savefig('16.png')
# plt.close('all')

# plot_MDP_in_environment(MDP_i,  1, action_list = [1,1,2,2,2,2])
# row_start,col = MDP_i.node_child(1,0,0)
# next_action_reward = MDP_i.values[row_start:(row_start+4),col]
# print('Action Costs 2: '+str(next_action_reward))
# plt.savefig('7.png')


# plot_MDP_in_environment(MDP_i,  1, action_list = [3,2,2,1,1,2])
# plot_MDP_in_environment(MDP_i,  1, action_list = [2,1,1,2,1,0])
# plot_MDP_in_environment(MDP_i,  1, action_list = [0,1,1,1,1,2])
# plot_MDP_in_environment(MDP_i,  1, action_list = [1,1,1,2,1,0])
# plot_MDP_in_environment(MDP_i,  1, action_list = [3,3,0,3,0,3])
# plot_MDP_in_environment(MDP_i,  1, action_list = [0,0,3,3,0,3])
# plot_MDP_in_environment(MDP_i,  1, action_list = [2,3,2,3,3,0])
plt.show()
