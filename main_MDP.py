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

minsub = 37
maxsub = 42
num_actions = 6
# 2a -- 1000simulations
# 3a -- 2000simulations
# 4a -- 4000simulations
# 6a -- 20000simulations
# MDP_simulations = 4000
MDP_simulations = 20000
# MDP_simulations = 2000
include_treasure = True

MDP_reward_model = 'max'
loop = True # loop through different numbers of simulations and #actions

###############################################################################
# Set up csv files
###############################################################################

def create_csv(filePath, columns):
    with open(filePath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(columns)

if loop:
    file = "raw_data/raw_data_MDP_parameters.csv"
    columns = ['Subject', 'Control', 'Complexity', 'Num_A', 'Num_sim', 'Regret_cum']
    create_csv(file, columns)
else:
    file = "raw_data/raw_data_MDP.csv"
    columns = ['Subject', 'Control', 'Complexity', 'Regret_cum']
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
    print('Selected Subject '+str(next_sub)+' for analysis')
    chosen_sub_list.append(next_sub)

    for num_a in range(1,7):
        if loop:
            num_sim_power = 0
            MDP_simulations = 1
            minsub = chosen_sub_list[-1]
            maxsub = chosen_sub_list[-1]
        while MDP_simulations < 30000:

            for sub in range(minsub, maxsub+1):
                found = False
                for i in range(len(skipped_subjects)):
                    if sub == skipped_subjects[i]:
                        found = True
                        continue
                if found is False:
                    if sub < 10:
                        subID = '0' + str(sub)
                    else:
                        subID = str(sub)
                else:
                    continue

                # Loop through trials
                for env in range(0, len(environments)):
                # for env in range(0, 1):
                    for con in range(0, len(control)):
                    # for con in range(0, 1):

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
                            if not include_treasure:
                                data.state.include_treasure = False
                            # Set initial parameters for looping through trials
                            trial_running = True
                            trial_time = 0
                            i = 0
                            intersection_t = []
                            regret = []

                            # Get initial state/observations from data
                            trial_time, player_action, observations = data.update_data_state(trial_time)
                            current_state = copy.deepcopy(data.state)

                            # Loop through the intersections in a trial
                            t_start = time.time()
                            while trial_running:

                                # Fill a markov decision process and get reward for the next step
                                next_action_reward, MDP_i = run_MDP(current_state,MDP_simulations,num_actions,MDP_reward_model)

                                # Simulate trial data forward until the player reaches an intersection
                                trial_time, player_action, observations = data.update_data_state(trial_time)

                                # Update State with new info for next iteration
                                continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,False)


                                # Store metrics from current intersection
                                player_action_reward = next_action_reward[player_action]
                                best_action_reward = np.amax(next_action_reward)
                                regret_i = best_action_reward-player_action_reward
                                max_regret_possible = best_action_reward - np.amin(next_action_reward)
                                best_action_dir = np.argmax(next_action_reward)
                                regret.append(regret_i)

                                # # Commented print outs
                                # print('Action Costs: '+str(next_action_reward))
                                # # print('Action Costs #2 : ', MDP_i.values[:16,1])
                                # print('Regret: '+str(regret_i))
                                # # plot_MDP_in_environment(MDP_i, 50)
                                # # if i % 4==0:
                                # #     plt.show()

                                if not continue_bool:
                                    break

                                i += 1

                            if not data.data_error:
                                # print(regret)
                                print('Took '+str((time.time()-t_start)/60)+' min')
                                if loop:
                                    row = [subID, control[con], environments[env],
                                            num_a, MDP_simulations, np.sum(regret)]

                                else:
                                    row = [subID, control[con], environments[env],
                                               np.sum(regret)]
                                with open(file, 'a') as csvfile:
                                    writer = csv.writer(csvfile, delimiter=',')
                                    writer.writerow(row)


            if loop:
                MDP_simulations_prev = MDP_simulations
                while MDP_simulations==MDP_simulations_prev:
                    num_sim_power += .25
                    MDP_simulations = int(np.round(np.e**num_sim_power))
            else:
                break
        if not loop:
            break

    if not loop:
        break
