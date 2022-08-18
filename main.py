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

minsub = 1
maxsub = 42
num_actions = 3
# 2a -- 1000simulations
# 3a -- 2000simulations
# 4a -- 4000simulations
# 6a -- 20000simulations
# num_sims = 4000
num_sims = 5000
# num_sims = 2000
POMDP_d = True
POMDP_obs = False
include_treasure = True

MDP_reward_model = 'mean'

###############################################################################
# Set up csv files
###############################################################################

def create_csv(filePath, columns):
    with open(filePath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(columns)

if POMDP_d:
    file_POMDP_d = "raw_data/raw_data_POMDP_d_"+str(num_actions)+'a_'+str(num_actions)+'s.csv'
    columns = ['Subject', 'Control', 'Complexity','Intersection_time','Regret','Maximum_Regret']

    # 'N_obs',
    #             'norm_mean', 'norm_cum','norm_path_mean', 'norm_path_cum', 'p_change_dir',
    #             'Reg_mean0', 'Reg_perc0','Reg_mean1', 'Reg_perc1',
    #             'Reg_mean2', 'Reg_perc2','Reg_mean3', 'Reg_perc3',
    #             'Regret_list','norm_list']
    create_csv(file_POMDP_d, columns)
# if POMDP_obs:


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
                # intersection_t = []
                # regret = []
                # if POMDP:
                #     regret_lists = []
                #     regret_percent_lists = []
                #     for i in range(4):
                #         regret_lists.append([])
                #         regret_percent_lists.append([])
                #     n_observations = 0
                #     # kl_obs = []
                #     norm_obs = []
                #     norm_path_obs = []
                #     change_dir_obs = []
                #     # kl_obs_cum = 0
                #     norm_obs_cum = 0
                #     norm_path_obs_cum = 0

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
                        # print('observations',observations)
                        # include_bool, norm, norm_cum = infomativeness_of_observations(current_state_no_observations,observations,num_sims,num_actions,MDP_reward_model)
                        include_bool, norm, norm_path, norm_cum, norm_path_cum, change_dir = infomativeness_of_observations(current_state_no_observations,observations,num_sims,num_actions,MDP_reward_model)
                        if include_bool:
                            # print(kl)
                            for i in range(norm.shape[0]):
                                # kl_obs.append(kl[i])
                                norm_obs.append(norm[i])
                                norm_path_obs.append(norm_path[i])
                                change_dir_obs.append(change_dir[i])
                            # kl_obs_cum += kl_cum
                            norm_obs_cum += norm_cum
                            norm_path_obs_cum += norm_path_cum

                    if POMDP_d:
                        # Fill a markov decision process and get reward for the next step
                        next_action_reward, MDP_i = run_MDP(current_state,num_sims,num_actions,MDP_reward_model)

                    # Simulate trial data forward until the player reaches an intersection
                    trial_time_current_iter = trial_time
                    trial_time, player_action, observations = data.update_data_state(trial_time)

                    # Update State with new info for next iteration
                    if POMDP_obs:
                        # copy previous current state, but do not include new observations
                        current_state_no_observations = copy.deepcopy(current_state)
                        continue_bool, current_state_no_observations = update_current_state_with_data(trial_time,data.state,current_state_no_observations,[],sub,POMDP_d)
                    continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,POMDP_d)


                    # Store metrics from current intersection
                    if POMDP_d:
                        player_action_reward = next_action_reward[player_action]
                        best_action_reward = np.amax(next_action_reward)
                        regret_i = best_action_reward-player_action_reward
                        max_regret_possible = best_action_reward - np.amin(next_action_reward)
                        best_action_dir = np.argmax(next_action_reward)
                        row = [subID, control[con], environments[env],
                                trial_time_current_iter, regret_i, max_regret_possible]
                        with open(file_POMDP_d, 'a') as csvfile:
                            writer = csv.writer(csvfile, delimiter=',')
                            writer.writerow(row)

                    # if POMDP:
                    #     for id in range(6):
                    #         for obs in observations:
                    #             if obs[1]==id and obs[2]==0.5:
                    #                 n_observations += 1
                    #                 break

                        # if max_regret_possible > 1 and max_regret_possible < 2:
                        #     regret.append(regret_i)
                        #     regret_percent.append(regret_i/max_regret_possible)

                        # regret.append(regret_i)
                        # if max_regret_possible >= .1 and max_regret_possible < .5:
                        #     regret_lists[0].append(regret_i)
                        #     regret_percent_lists[0].append(regret_i/max_regret_possible)
                        # elif max_regret_possible >= .5 and max_regret_possible < 1:
                        #     regret_lists[1].append(regret_i)
                        #     regret_percent_lists[1].append(regret_i/max_regret_possible)
                        # elif max_regret_possible >= 1 and max_regret_possible < 2:
                        #     regret_lists[2].append(regret_i)
                        #     regret_percent_lists[2].append(regret_i/max_regret_possible)
                        # elif max_regret_possible >= 2:
                        #     regret_lists[3].append(regret_i)
                        #     regret_percent_lists[3].append(regret_i/max_regret_possible)


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
                    if POMDP_d:
                        print(regret)
                        print(norm_obs)
                    else:
                        print(regret)
                    print('Took '+str((time.time()-t_start)/60)+' min')
                    # if POMDP:
                    #     regret_mean = np.zeros(4)
                    #     regret_percent = np.zeros(4)
                    #     for i in range(4):
                    #         if len(regret_lists[i])<1:
                    #             regret_mean[i] = np.nan
                    #             regret_percent[i] = np.nan
                    #         else:
                    #             regret_mean[i] = np.mean(regret_lists[i])
                    #             regret_percent[i] = np.mean(regret_percent_lists[i])
                    #     if len(norm_obs)<1:
                    #         # kl_mean = np.nan
                    #         norm_mean = np.nan
                    #         norm_path_mean = np.nan
                    #         p_change_dir = np.nan
                    #     else:
                    #         # kl_mean = np.mean(kl_obs)
                    #         norm_mean = np.mean(norm_obs)
                    #         norm_path_mean = np.mean(norm_path_obs)
                    #         p_change_dir = np.mean(change_dir_obs)
                    #     # row = [subID, control[con], environments[env], n_observations,
                    #     #       norm_mean, norm_obs_cum, regret_mean[0], regret_percent[0],
                    #     #       regret_mean[1], regret_percent[1],regret_mean[2], regret_percent[2],
                    #     #       regret_mean[3], regret_percent[3], regret, norm_obs]
                    #     row = [subID, control[con], environments[env], n_observations,
                    #         norm_mean, norm_obs_cum, norm_path_mean, norm_path_obs_cum, p_change_dir,
                    #         regret_mean[0], regret_percent[0],regret_mean[1], regret_percent[1],
                    #         regret_mean[2], regret_percent[2],regret_mean[3], regret_percent[3],
                    #         regret, norm_obs]
                    # else:
                    #     row = [subID, control[con], environments[env],
                    #            np.sum(regret)]
                    # with open(file, 'a') as csvfile:
                    #     writer = csv.writer(csvfile, delimiter=',')
                    #     writer.writerow(row)
