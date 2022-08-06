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

# for pomdps, if the player sees the agent, account for the
# chance it is not an adversary

minsub = 15
maxsub = 22
num_actions = 3
# 2a -- 1000simulations
# 4a -- 4000simulations
# 6a -- 20000simulations
# MDP_simulations = 4000
MDP_simulations = 2000
# MDP_simulations = 2000
POMDP = True
POMDP_seperate_observations = True
include_treasure = False

MDP_reward_model = 'max'
if POMDP:
    MDP_reward_model = 'mean'

###############################################################################
# Set up csv files
###############################################################################

def create_csv(filePath, columns):
    with open(filePath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(columns)

file = "raw_data/raw_data_MDP.csv"
columns = ['Subject', 'Control', 'Complexity', 'Regret_cum']
if POMDP:
    file = "raw_data/raw_data_POMDP.csv"
    columns = ['Subject', 'Control', 'Complexity','N_obs',
                'Regret_mean', 'Regret_perc_mean','norm_mean',
                'norm_cum','Regret_list','norm_list']

    # create_csv(file, columns)

file_missingbags = "raw_data/unparsable_bags_playback.csv"
columns = ['Subject', 'Control', 'Complexity']
# create_csv(file_missingbags, columns)


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
                if not include_treasure:
                    data.state.include_treasure = False
                # Set initial parameters for looping through trials
                trial_running = True
                trial_time = 0
                i = 0
                intersection_t = []
                regret = []
                if POMDP:
                    regret_percent = []
                    n_observations = 0
                    # kl_obs = []
                    norm_obs = []
                    # kl_obs_cum = 0
                    norm_obs_cum = 0

                # Get initial state/observations from data
                trial_time, player_action, observations = data.update_data_state(trial_time)
                current_state = copy.deepcopy(data.state)
                if POMDP:
                    # clear state knowledge of adversary locations
                    current_state.adversaries = []
                    current_state.partially_observable = True
                    if POMDP_seperate_observations:
                        current_state_no_observations = copy.deepcopy(current_state)
                        current_state_no_observations.update_state_with_observations([])

                    current_state.update_state_with_observations(observations)

                # Loop through the intersections in a trial
                t_start = time.time()
                while trial_running:

                    if POMDP_seperate_observations and con!=0: #for none, there are no drone observations
                        # print('observations',observations)
                        include_bool, norm, norm_cum = infomativeness_of_observations(current_state_no_observations,observations,MDP_simulations,num_actions,MDP_reward_model)
                        if include_bool:
                            # print(kl)
                            for i in range(norm.shape[0]):
                                # kl_obs.append(kl[i])
                                norm_obs.append(norm[i])
                            # kl_obs_cum += kl_cum
                            norm_obs_cum += norm_cum

                    # Fill a markov decision process and get reward for the next step
                    next_action_reward, MDP_i = run_MDP(current_state,MDP_simulations,num_actions,MDP_reward_model)

                    # Simulate trial data forward until the player reaches an intersection
                    trial_time, player_action, observations = data.update_data_state(trial_time)

                    # Update State with new info for next iteration
                    if POMDP_seperate_observations:
                        # copy previous current state, but do not include new observations
                        current_state_no_observations = copy.deepcopy(current_state)
                        continue_bool, current_state_no_observations = update_current_state_with_data(trial_time,data.state,current_state_no_observations,[],sub,POMDP)
                    continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,POMDP)


                    # Store metrics from current intersection
                    player_action_reward = next_action_reward[player_action]
                    best_action_reward = np.amax(next_action_reward)
                    regret_i = best_action_reward-player_action_reward
                    max_regret_possible = best_action_reward - np.amin(next_action_reward)
                    best_action_dir = np.argmax(next_action_reward)
                    if POMDP:
                        for id in range(6):
                            for obs in observations:
                                if obs[1]==id and obs[2]==0.5:
                                    n_observations += 1
                                    break

                        if max_regret_possible > 1 and max_regret_possible < 2:
                            regret.append(regret_i)
                            regret_percent.append(regret_i/max_regret_possible)
                    else:
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
                    if POMDP:
                        print(regret)
                        print(norm_obs)
                        print(len(norm_obs))
                    else:
                        print(regret)
                    print('Took '+str((time.time()-t_start)/60)+' min')
                    if POMDP:
                        if len(regret)<1:
                            regret_mean = np.nan
                            regret_percent = np.nan
                        else:
                            regret_mean = np.mean(regret)
                            regret_percent = np.mean(regret_percent)
                        if len(norm_obs)<1:
                            # kl_mean = np.nan
                            norm_mean = np.nan
                        else:
                            # kl_mean = np.mean(kl_obs)
                            norm_mean = np.mean(norm_obs)

                        row = [subID, control[con], environments[env], n_observations,
                              regret_mean, regret_percent, norm_mean,
                              norm_obs_cum, regret, norm_obs]
                    else:
                        row = [subID, control[con], environments[env],
                               np.sum(regret)]
                    with open(file, 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow(row)
