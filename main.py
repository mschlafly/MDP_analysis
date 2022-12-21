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

minsub = 36
maxsub = 42
num_actions = 6
num_sims = 10000
POMDP_d = False  # Boolean for whether to compare the player and optimal agent's decisions
POMDP_obs = False # Boolean for whether to to determine how helpful each observation is
save_data = True
include_treasure = True

if POMDP_d or POMDP_obs:
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

if POMDP_d:
    file_POMDP_d = "raw_data/raw_data_POMDP_d_"+str(num_actions)+'a_'+str(num_sims)+'s.csv'
    columns = ['Subject', 'Control', 'Complexity','Expertise','Intersection_time','Regret','Maximum_Regret']
    create_csv(file_POMDP_d, columns)
if POMDP_obs:
    file_POMDP_obs_i = "raw_data/raw_data_POMDP_obs_i_"+str(num_actions)+'a_'+str(num_sims)+'s.csv'
    file_POMDP_obs_cum = "raw_data/raw_data_POMDP_obs_cum_"+str(num_actions)+'a_'+str(num_sims)+'s.csv'
    columns = ['Subject', 'Control', 'Complexity','Expertise','Intersection_time','P_switch',
                'norm_mean','norm_bestpath','norm_userpath']
    create_csv(file_POMDP_obs_i, columns)
    columns = ['Subject', 'Control', 'Complexity','Expertise','Intersection_time','P_switch_cum',
                'norm_cum','norm_bestpath_cum','norm_userpath_cum']
    create_csv(file_POMDP_obs_cum, columns)
if not (POMDP_d or POMDP_obs):
    file = "raw_data/raw_data_MDP_"+str(num_actions)+'a_'+str(num_sims)+'s.csv'
    columns = ['Subject', 'Control', 'Complexity', 'MDP_r']
    # create_csv(file, columns)

file_missingbags = "raw_data/unparsable_bags_playback.csv"
columns = ['Subject', 'Control', 'Complexity']
create_csv(file_missingbags, columns)


###############################################################################
# Determine what subjects to include
###############################################################################

# Specify specific subjects to skip here.
# incomplete subjects and novices
skipped_subjects = [2, 3, 4, 5, 6, 7, 10, 12, 16, 23, 30, 31, 33, 38, 39, 42]

# # incomplete subjects and experts
# skipped_subjects = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
#         20, 21, 22, 24, 25, 26, 27, 28, 29, 32, 34, 35, 36, 37, 40, 41]

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
    if np.isin(sub,[7,23,30,31,33,38,39,42]):
        expertise = 'novice'
    else:
        expertise = 'expert'

    # Loop through trials
    for env in range(0, len(environments)):
        for con in range(0, len(control)):

            if sub==36:
                if env==0:
                    continue
                else:
                    if con==0 or con==1:
                        continue

            # skip if only testing the impact of drone observations
            if POMDP_obs and (POMDP_d==False) and con==0:
                continue

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
                regret_cum = []

                # Get initial state/observations from data
                trial_time, player_action, observations = data.update_data_state(trial_time)
                current_state = copy.deepcopy(data.state)
                if POMDP_d or POMDP_obs:
                    # clear state knowledge of adversary locations
                    current_state.adversaries = []
                    current_state.partially_observable = True
                    if POMDP_obs:
                        current_state_no_observations = copy.deepcopy(current_state)
                        current_state_no_observations.update_state_with_observations([])

                    current_state.update_state_with_observations(observations)

                # Loop through the intersections in a trial
                t_start = time.time()
                while trial_running:

                    if POMDP_obs and con!=0: #for none, there are no drone observations
                        infomativeness_of_observations(current_state_no_observations,
                                observations,num_sims,num_actions,MDP_reward_model,
                                file_POMDP_obs_i,file_POMDP_obs_cum,
                                [subID, control[con], environments[env], expertise],copy.deepcopy(data))

                    # Fill a markov decision process and get reward for the next step
                    if POMDP_d:
                        next_action_reward, MDP_i = run_MDP(current_state,num_sims,num_actions,MDP_reward_model)
                    elif not POMDP_obs:
                        next_action_reward, MDP_i = run_MDP(current_state,num_sims,num_actions,MDP_reward_model)


                    # Simulate trial data forward until the player reaches an intersection
                    trial_time_current_iter = trial_time
                    trial_time, player_action, observations = data.update_data_state(trial_time)
                    print(trial_time)

                    # Update State with new info for next iteration
                    if POMDP_obs:
                        # copy previous current state, but do not include new observations
                        current_state_no_observations = copy.deepcopy(current_state)
                        continue_bool, current_state_no_observations = update_current_state_with_data(trial_time,data.state,current_state_no_observations,[],sub,True)
                    elif POMDP_d:
                        continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,True)
                    else:
                        continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,False)


                    # Store metrics from current intersection
                    if not POMDP_obs:
                        player_action_reward = next_action_reward[player_action]
                        best_action_reward = np.amax(next_action_reward)
                        regret_i = best_action_reward-player_action_reward
                        # print(next_action_reward, regret_i)
                        if POMDP_d:
                            max_regret_possible = best_action_reward - np.amin(next_action_reward)
                            row = [subID, control[con], environments[env], expertise,
                                    trial_time_current_iter, regret_i, max_regret_possible]
                            if save_data:
                                with open(file_POMDP_d, 'a') as csvfile:
                                    writer = csv.writer(csvfile, delimiter=',')
                                    writer.writerow(row)
                        else:
                            regret_cum.append(regret_i)
                        # Commented print outs
                        # print(len(MDP_i.state_init.adversaries))
                        # print('Action Costs: '+str(next_action_reward))
                        # # print('Action Costs #2 : ', MDP_i.values[:16,1])
                        # print('Regret: '+str(regret_i))
                        # # plot_MDP_in_environment(MDP_i,  50)
                        # # plt.show()

                    if not continue_bool:
                        break

                    i += 1

                if not data.data_error:
                    print('Took '+str((time.time()-t_start)/60)+' min')
                    if not (POMDP_d or POMDP_obs):
                        row = [subID, control[con], environments[env],
                               np.sum(regret_cum)]
                        with open(file, 'a') as csvfile:
                            writer = csv.writer(csvfile, delimiter=',')
                            writer.writerow(row)
