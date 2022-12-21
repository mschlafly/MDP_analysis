# This script stores the regret metric for increasing numbers of actions and simulations
# This is used to determint the parameters for the model convergence

from read_data import trial_data
from main_utils import *
from env_utils import environment
from plot_MDP import plot_MDP_in_environment
import copy
import matplotlib.pyplot as plt
import csv
import numpy as np
import time

###############################################################################
# Parameters
###############################################################################
POMDP = True # True means POMDP model; False is MDP model
include_treasure = True
if POMDP:
    MDP_reward_model = 'mean'
else:
    MDP_reward_model = 'max'

###############################################################################
# Set up csv files
###############################################################################

def create_csv(filePath, columns):
    with open(filePath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(columns)

if POMDP:
    file = "raw_data/raw_data_POMDP_parameters.csv"
    columns = ['Subject', 'Control', 'Complexity', 'Num_A', 'Num_sim', 'Intersection_time', 'Regret']
    create_csv(file, columns)
else:
    file = "raw_data/raw_data_MDP_parameters.csv"
    columns = ['Subject', 'Control', 'Complexity', 'Num_A', 'Num_sim', 'Intersection_time', 'Regret']
    create_csv(file, columns)

file_missingbags = "raw_data/unparsable_bags_playback.csv"
columns = ['Subject', 'Control', 'Complexity']
create_csv(file_missingbags, columns)


###############################################################################
# Determine what subjects to include
###############################################################################

# Specify specific subjects to skip here.
# incomplete subjects and novices
skipped_subjects = [2, 3, 4, 5, 6, 7, 10, 12, 16, 23, 30, 31, 33, 38, 39, 42]

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

# Loop through subjects, #actions, #sims
chosen_sub_list = []
while len(chosen_sub_list)<3:
    # Randomly select subject for experiment
    next_sub = int(np.random.choice(np.linspace(1,42,42)))

    # Check if the subject is OK to use
    found = False
    for i in range(len(skipped_subjects)):
        if next_sub == skipped_subjects[i]:
            found = True
            continue
    for i in range(len(chosen_sub_list)):
        if next_sub==chosen_sub_list[i]:
            found = True
            continue
    if found:
        continue
    # next_sub = 13
    print('Selected Subject '+str(next_sub)+' for analysis')
    chosen_sub_list.append(next_sub)

    intersection_time = np.random.randint(0,60*3,(2,5))

    # intersection_time = np.array([[101,  53,   4,  41 ,162],[123 ,130  ,56 ,132 , 74]])
    # intersection_time = np.array([[ 52 ,101 , 90 ,174 ,164],[ 19, 149 , 77 , 84 , 56]]) #13
    print(intersection_time)

    sub = next_sub
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
            data = trial_data(readDataDIR,sub,con,env)
            if data.data_error:
                print('Data was unable to be imported correctly')
                row = [subID, control[con], environments[env]]
                with open(file_missingbags, 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow(row)
            else:
                if not include_treasure:
                    data.state.include_treasure = False

                # Set initial parameters for looping through trials
                trial_running = True
                trial_time = 0
                i = 0

                # Get initial state/observations from data
                trial_time, player_action, observations = data.update_data_state(trial_time)
                current_state = copy.deepcopy(data.state)
                if POMDP:
                    # clear state knowledge of adversary locations
                    current_state.adversaries = []
                    current_state.partially_observable = True
                    current_state.update_state_with_observations(observations)

                # Loop through the intersections in a trial
                t_start = time.time()
                while trial_time<intersection_time[env,con]:
                    # Simulate trial data forward until the player reaches an intersection
                    trial_time_current_iter = trial_time
                    trial_time, player_action, observations = data.update_data_state(trial_time)

                # Update State with new info for next iteration
                continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,POMDP)

                # Simulate trial data forward until the player reaches an intersection
                trial_time_current_iter = trial_time
                trial_time, player_action, observations = data.update_data_state(trial_time)

                for num_a in [3,4,5,6,8,10]:

                    # Create MDP
                    MDP_i = MDP(copy.deepcopy(current_state),num_a,MDP_reward_model)

                    num_sim_power = 0
                    num_sims = 1
                    minsub = chosen_sub_list[-1]
                    maxsub = chosen_sub_list[-1]

                    end_sim = 25000
                    if num_a < 4:
                        end_sim = 10000
                    num_sims_prev = 0
                    while num_sims < end_sim:
                        new_num_sims = num_sims - num_sims_prev

                        # Fill a markov decision process and get reward for the next step
                        MDP_i.populate_tree_parallelized(new_num_sims)

                        # Determine value for current number of sims by copying
                        MDP_i_iter = copy.deepcopy(MDP_i)
                        next_action_reward = MDP_i_iter.update_value_tree()


                        # Store metrics from current intersection
                        player_action_reward = next_action_reward[player_action]
                        best_action_reward = np.amax(next_action_reward)
                        regret_i = best_action_reward-player_action_reward

                        if POMDP:
                            row = [subID, control[con], environments[env],
                                    num_a, num_sims, trial_time_current_iter, regret_i]
                        else:
                            row = [subID, control[con], environments[env],
                                    num_a, num_sims, trial_time_current_iter, regret_i]

                        with open(file, 'a') as csvfile:
                            writer = csv.writer(csvfile, delimiter=',')
                            writer.writerow(row)


                        num_sims_prev = num_sims
                        while num_sims==num_sims_prev:
                            num_sim_power += .25
                            num_sims = int(np.round(np.e**num_sim_power))


                if not data.data_error:
                    print('Took '+str((time.time()-t_start)/60)+' min for trial')
