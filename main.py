from read_data import trial_data
from MDP_class import MDP
from env_utils import environment
from plot_MDP import plot_MDP_in_environment
import copy
import matplotlib.pyplot as plt
import csv
import numpy as np


###############################################################################
# Parameters
###############################################################################

minsub = 1
maxsub = 42
MDP_simulations = 15000
MDP_simulations = 100
# 4a -- 4000simulations
MDP_simulations = 4000
# MDP_simulations = 1000
POMDP = False


###############################################################################
# Set up csv files
###############################################################################

def create_csv(filePath, columns):
    with open(filePath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(columns)

file = "raw_data/raw_data_MDP.csv"
columns = ['Subject', 'Control', 'Complexity', 'Regret_cum']
# create_csv(file, columns)

file_missingbags = "raw_data/unparsable_bags_playback.csv"
columns = ['Subject', 'Control', 'Complexity']
# create_csv(file_missingbags, columns)


###############################################################################
# Determine what subjects to include
###############################################################################

# Specify specific subjects to skip here.
skipped_subjects = []

environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

###############################################################################
# Decide  folder where to save the data
###############################################################################

writeDataDIR = 'raw_data/'
readDataDIR = 'raw_data/playback/'


###############################################################################
# Main script
###############################################################################


for sub in range(minsub, maxsub+1):
    found = False
    for i in range(len(skipped_subjects)):
        if sub == skipped_subjects[i]:
            found = True
    if found is False:
        if sub < 10:
            subID = '0' + str(sub)
        else:
            subID = str(sub)

    # Loop through trials
    for env in range(0, len(environments)):
        for con in range(0, len(control)):
            trialInfo = subID + '_' + control[con] + '_' + environments[env]
            print(trialInfo)

            # Initialize data object
            data = trial_data(readDataDIR,sub,con,env,print=False)

            if data.data_error:
                print('Data was unable to be imported correctly')
                row = [subID, control[con], environments[env]]
                with open(file_missingbags, 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow(row)
            else:

                # Set initial parameters for looping through trials
                trial_running = True
                trial_time = 0
                i = 0
                intersection_t = []
                regret = []

                # Get initial state/observations from data
                trial_time, player_action, observations = data.update_data_state(trial_time)
                current_state = copy.deepcopy(data.state)
                if POMDP:
                    # clear state knowledge of adversary locations
                    current_state.adversaries = []

                    current_state.partially_observable = True
                    current_state.update_state_with_observations(observations)

                # Loop through the intersections in a trial
                while trial_running:

                    # Initialize and fill the MDP, then update rewards using Bellman equation
                    MDP_i = MDP(current_state)
                    MDP_i.populate_tree_parallelized(MDP_simulations)
                    MDP_i.update_value_tree()
                    next_action_reward = MDP_i.values[:4,0]

                    # Simulate trial data forward until the player reaches an intersection
                    trial_time, player_action, observations = data.update_data_state(trial_time)

                    # Add regret from current intersection
                    player_action_reward = next_action_reward[player_action]
                    best_action_reward = np.amax(next_action_reward)
                    best_action_dir = np.argmax(next_action_reward)
                    regret.append(best_action_reward-player_action_reward)


                    # Commented print outs
                    # print('Action Costs: '+str(next_action_reward),np.sum(next_action_reward))
                    # # print('Action Costs #2 : ', MDP_i.values[:16,1])
                    # print('Regret: '+str(best_action_reward-player_action_reward))
                    # plot_MDP_in_environment(MDP_i, 50)
                    # if i % 2==0:
                    #     plt.show()


                    # Update State with new info for next iteration
                    if sub==17 or sub==18:
                        if trial_time>60*5-45:
                            break
                    if trial_time>60*5-30:
                        break
                    # print('Next Intersection at '+str(trial_time)+' sec')
                    if POMDP:
                        current_state.player = copy.deepcopy(data.state.player)
                        current_state.treasure = copy.deepcopy(data.state.treasure)
                        current_state.game_time_data = trial_time
                        current_state.update_state_with_observations(observations)
                    else:
                        current_state = copy.deepcopy(data.state)

                    i += 1

                if not data.data_error:
                    print(regret)
                    row = [subID, control[con], environments[env],
                           np.sum(regret)]
                    # row = [subID, control[con], environments[env],
                    #       np.mean(regret), regret]
                    with open(file, 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow(row)
