from read_data import trial_data
from main_utils import *
from env_utils import environment
from plot_MDP import plot_MDP_in_environment
import copy
import matplotlib.pyplot as plt
import csv
import numpy as np
import time
from numpy.random import choice

###############################################################################
# Parameters
###############################################################################
#  skipped_subjects = [2, 3, 4, 5, 6, 7, 10, 12, 16, 23, 30, 31, 33, 38, 39, 42]
minsub = 29
maxsub = 29
env = 0
con = 4
num_actions = 6
num_sims = 30000
num_decisions_in_plot = 6
num_paths_in_plot = 100
num_decisions_skip = 4
POMDP_d = True

y_lim_min = -8#-4
y_lim_max = .5#1.5

include_treasure = True
MDP_reward_model = 'mean'

environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

skipped_subjects = [2, 3, 4, 5, 6, 7, 10, 12, 16, 23, 30, 31, 33, 38, 39, 42]

###############################################################################
# Functions
###############################################################################

def curved_plot(x1,x2,y1,y2):
    expected_reward = y2-y1
    slope = (y2-y1)/(x2-x1)
    x3 = x2 + 1
    y3 = y2 #+ (slope*.9)*(x3-x2)

    x_points = [x1,x2,x3]
    y_points = [y1,y2,y3]

    z = np.polyfit(x_points,y_points,2)
    p = np.poly1d(z)

    x = np.linspace(x1,x2,30)
    y = p(x)
    return x,y


###############################################################################
# Set up figure
###############################################################################
figure_size = (6,3)
fig, ax = plt.subplots(figsize=figure_size, dpi=300)
linewidth = 1

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


    # Initialize data object
    readDataDIR = 'raw_data/playback/'
    trialInfo = subID + '_' + control[con] + '_' + environments[env]
    print(trialInfo)
    data = trial_data(readDataDIR,sub,con,env,print=False)

    if data.data_error:
        print('Data was unable to be imported correctly')
        continue
    else:
        if not include_treasure:
            data.state.include_treasure = False


    # Set initial parameters for looping through intersections
    # trial_running = True
    trial_time = 0
    i = 0

    # Get initial state/observations from data
    trial_time, player_action, observations = data.update_data_state(trial_time)
    current_state_partial_info = copy.deepcopy(data.state)
    # clear state knowledge of adversary locations
    current_state_partial_info.adversaries = []
    current_state_partial_info.partially_observable = True
    current_state_partial_info.update_state_with_observations(observations)

    current_state_all_state_info = copy.deepcopy(data.state)
    starting_game_score = data.game_score_unofficial
    game_score_current = starting_game_score

    # Loop through the intersections in a trial
    decision = 0
    current_expected_reward = 0
    while decision<num_decisions_skip+num_decisions_in_plot:
        print('Decision: '+str(decision)+' Current Game Time: ' + str(trial_time))
        print('Game Score: '+str(game_score_current))
        if decision >= num_decisions_skip:
            # Fill a markov decision process and get reward for the next step
            next_action_reward, MDP_i = run_MDP(current_state_partial_info,num_sims,num_actions,MDP_reward_model)
            # _, MDP_i_all_state_info = run_MDP(current_state_all_state_info,num_sims,num_actions,MDP_reward_model)

        # Simulate trial data forward until the player reaches an intersection
        trial_time_current_iter = trial_time
        game_score_current = data.game_score_unofficial
        trial_time, player_action, observations = data.update_data_state(trial_time)


        # Get the next 6 player actions
        if decision >= num_decisions_skip:
            next_6_player_actions = [player_action]
            trial_time_get_action = trial_time
            data_temp = copy.deepcopy(data)
            for i in range(num_actions-1):
                trial_time_get_action, player_action, _ = data_temp.update_data_state(trial_time_get_action)
                next_6_player_actions.append(player_action)

        # Update State with new info for next iteration

        observation_sight = []
        for obs in observations:
            # game_time, agent_id, probability_observed, pos_x, pos_y, action, chasing_bool, ignore]
            if obs[2]>.75:
                observation_sight.append(obs)

        # _, current_state_partial_info = update_current_state_with_data(trial_time,data.state,current_state_partial_info,observations,sub,True)
        _, current_state_partial_info = update_current_state_with_data(trial_time,data.state,current_state_partial_info,observation_sight,sub,True)
        # _, current_state_all_state_info = update_current_state_with_data(trial_time,data.state,current_state_all_state_info,observations,sub,False)

        if decision < num_decisions_skip:
            starting_game_score = data.game_score_unofficial
            decision += 1
            continue

        # Plot spotted adversaries
        # print(observations)
        # [game_time, agent_id, probability_observed, pos_x, pos_y, action, chasing_bool, ignore]
        for obs in observations:
            # x_pos = decision + (obs[0]-trial_time_current_iter)/(trial_time-trial_time_current_iter)
            x_pos = obs[0]
            if obs[2]>0.6:
                ax.plot([x_pos,x_pos],[y_lim_min,y_lim_max],linestyle='-',
                color='#ffe680ff', linewidth=linewidth)
            else:
                ax.plot([x_pos,x_pos],[y_lim_min,y_lim_max],linestyle='--',
                color='#ffe680ff', linewidth=linewidth)

        # # Plot game score
        # if data.game_score_unofficial!=game_score_current:
        #     game_score_current = data.game_score_unofficial
        #     ax.plot([trial_time_current_iter,data.game_time_score_change],
        #             [game_score_current-starting_game_score,game_score_current-starting_game_score],
        #             linestyle='-', color='#0136FF', linewidth=linewidth)
        #     ax.plot([data.game_time_score_change,data.game_time_score_change],
        #             [game_score_current-starting_game_score,data.game_score_unofficial-starting_game_score],
        #             linestyle='-', color='#0136FF', linewidth=linewidth)
        #     ax.plot([data.game_time_score_change,trial_time],
        #             [data.game_score_unofficial-starting_game_score,data.game_score_unofficial-starting_game_score],
        #             linestyle='-', color='#0136FF', linewidth=linewidth)
        # else:
        #     ax.plot([trial_time_current_iter,trial_time],[game_score_current-starting_game_score,game_score_current-starting_game_score],
        #             linestyle='-', color='#0136FF', linewidth=linewidth)


        ###############################################################################
        # Plot expected reward for current intersection/decision
        ###############################################################################

        # Loop through and plot 6-action paths
        while i < num_paths_in_plot:
            for a_i in range(num_actions):
                action = choice([0,1,2,3])
                if a_i==0:
                    # set position of the first child state
                    row = action; col = 0
                    # expected_reward = MDP_i.values[row,col]
                else:
                    # Get the grid position of the next state
                    row,col = MDP_i.node_child(row,col,action)
            expected_reward = MDP_i.values[row,col]
            if expected_reward!=-50:
                x,y = curved_plot(trial_time_current_iter,trial_time,current_expected_reward,current_expected_reward+expected_reward)
                ax.plot(x,y,linestyle='-',
                        color='#a6a6a6ff', linewidth=linewidth/2)
                # ax.plot([trial_time_current_iter,trial_time],[current_expected_reward,current_expected_reward+expected_reward],linestyle='-',
                #         color='#a6a6a6ff', linewidth=linewidth)
                i += 1

        # ###############################################################################
        # # Plot expected reward for all information
        # ###############################################################################
        #
        # # plot path with highest expected reward
        # for a_i in range(num_actions):
        #     if a_i==0:
        #         # set position of the first child state
        #         rewards_next_action = MDP_i_all_state_info.values[0:(0+4),0]
        #         best_action_dir = np.argmax(rewards_next_action, axis=0)
        #         # print(rewards_next_action,best_action_dir)
        #         row = best_action_dir; col = 0
        #     else:
        #         # Get the grid position of the next state
        #         row,col = MDP_i_all_state_info.node_child(row,col,0)
        #         rewards_next_action = MDP_i_all_state_info.values[row:(row+4),col]
        #         best_action_dir = np.argmax(rewards_next_action, axis=0)
        #         # print(rewards_next_action,best_action_dir)
        #         row = row + best_action_dir
        # expected_reward = MDP_i_all_state_info.values[row,col]
        # expected_reward = np.max(MDP_i_all_state_info.values[:,-1])
        # # print(expected_reward)
        # if expected_reward!=-50:
        #     x,y = curved_plot(trial_time_current_iter,trial_time,current_expected_reward,current_expected_reward+expected_reward)
        #     ax.plot(x,y,linestyle='--',
        #             color='#ff00ffff', linewidth=linewidth)
        #
        # # plot player path next_6_player_actions
        # for a_i in range(num_actions):
        #     if a_i==0:
        #         # set position of the first child state
        #         row = next_6_player_actions[a_i]; col = 0
        #     else:
        #         # Get the grid position of the next state
        #         row,col = MDP_i_all_state_info.node_child(row,col,next_6_player_actions[a_i])
        #     # print(next_6_player_actions[a_i],row,col,MDP_i.values[row,col])
        # expected_reward = MDP_i_all_state_info.values[row,col]
        # if expected_reward==-50:
        #     print('ERROR: not enough samples')
        # else:
        #     x,y = curved_plot(trial_time_current_iter,trial_time,current_expected_reward,current_expected_reward+expected_reward)
        #     ax.plot(x,y,linestyle='--',
        #             color='#39FF14', linewidth=linewidth)

        ###############################################################################
        # Plot expected reward for partial information
        ###############################################################################

        # plot path with highest expected reward
        for a_i in range(num_actions):
            if a_i==0:
                # set position of the first child state
                rewards_next_action = MDP_i.values[0:(0+4),0]
                best_action_dir = np.argmax(rewards_next_action, axis=0)
                # print(rewards_next_action,best_action_dir)
                row = best_action_dir; col = 0
            else:
                # Get the grid position of the next state
                row,col = MDP_i.node_child(row,col,0)
                rewards_next_action = MDP_i.values[row:(row+4),col]
                best_action_dir = np.argmax(rewards_next_action, axis=0)
                # print(rewards_next_action,best_action_dir)
                row = row + best_action_dir
        expected_reward = MDP_i.values[row,col]
        expected_reward = np.max(MDP_i.values[:,-1])
        # print(expected_reward)
        if expected_reward!=-50:
            x,y = curved_plot(trial_time_current_iter,trial_time,current_expected_reward,current_expected_reward+expected_reward)
            ax.plot(x,y,linestyle='-',
                    color='#ff00ffff', linewidth=linewidth)

        # plot player path next_6_player_actions
        for a_i in range(num_actions):
            if a_i==0:
                # set position of the first child state
                row = next_6_player_actions[a_i]; col = 0
            else:
                # Get the grid position of the next state
                row,col = MDP_i.node_child(row,col,next_6_player_actions[a_i])
            # print(next_6_player_actions[a_i],row,col,MDP_i.values[row,col])
        expected_reward = MDP_i.values[row,col]
        if expected_reward==-50:
            print('ERROR: not enough samples')
        else:
            x,y = curved_plot(trial_time_current_iter,trial_time,current_expected_reward,current_expected_reward+expected_reward)
            ax.plot(x,y,linestyle='-',
                    color='#39FF14', linewidth=linewidth)

        current_expected_reward += expected_reward
        decision += 1
title = ''
xlabel = 'Trial Time (s)'
ylabel = 'Change in Expected Reward'
plt.xlabel(xlabel, fontname="sans-serif", fontsize=9)
plt.ylabel(ylabel, fontname="sans-serif", fontsize=9)
plt.title(title, fontname="sans-serif", fontsize=9, fontweight='bold')
for label in (ax.get_xticklabels()):
    label.set_fontsize(8)
for label in (ax.get_yticklabels()):
    label.set_fontsize(8)
ax.set_ylim([y_lim_min,y_lim_max])
fig.savefig('Plots/possible_paths_sub'+subID+'_con'+str(con)+'_withoutsensoryaugmentation.pdf')
# fig.savefig('Plots/possible_paths_sub'+subID+'_con'+str(con)+'.pdf')

plt.show()
