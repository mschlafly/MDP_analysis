from MDP_class import MDP
import numpy as np
import copy
from plot_MDP import plot_MDP_in_environment
import matplotlib.pyplot as plt
import csv


def run_MDP(current_state,MDP_simulations,num_player_actions,MDP_reward_model):
    # Initialize and fill the MDP, then update rewards using Bellman equation
    MDP_i = MDP(copy.deepcopy(current_state),num_player_actions,MDP_reward_model)
    MDP_i.populate_tree_parallelized(MDP_simulations)
    next_action_reward = MDP_i.update_value_tree()
    return next_action_reward, MDP_i

def update_current_state_with_data(trial_time,data_state,current_state,observations,sub,POMDP):

    if sub==17 or sub==18:
        if trial_time>60*5-45:
            return False, current_state
    if trial_time>60*5-30:
        return False, current_state

    if POMDP:
        current_state.player = copy.deepcopy(data_state.player)
        current_state.treasure = copy.deepcopy(data_state.treasure)
        current_state.game_time_data = trial_time
        current_state.update_state_with_observations(observations)
    else:
        current_state = copy.deepcopy(data_state)

    return True, current_state

def kl_divergence(new_dist,dist):
    # relative entropy between new_dist and dist
    # assume equal size
    #     new_dist = [.5, .5, .5, .5]
    # else:
    #     new_dist /= norm

    norm = np.linalg.norm(new_dist)
    if norm==0:
        new_dist = [.5, .5, .5, .5]
    else:
        new_dist = 0.5 + new_dist/(norm*2.1)
    norm = np.linalg.norm(dist)
    if norm==0:
        dist = [.5, .5, .5, .5]
    else:
        dist = 0.5 + dist/(norm*2.1)
    # for i in range(len(new_dist)):
    #     if new_dist[i]==0:
    #         new_dist[i] = np.random.normal(0,scale=.1)
    #         if dist[i]==0:
    #             dist[i] = np.random.normal(0,scale=.1)    # if norm==0:
    # if norm==0:
    #     new_dist = [.5, .5, .5, .5]
    # else:
    #     dist /= norm

    kl = 0
    for i in range(len(dist)):
        # print(new_dist[i],dist[i])
        # print(new_dist[i]/dist[i])
        # print(np.log2(new_dist[i]/dist[i]))
        kl += new_dist[i] * np.log2(new_dist[i]/dist[i])
    return abs(kl)

def l2_norm(new_vec,vec):
    # assume equal size
    return np.linalg.norm(new_vec-vec)

def best_path_norm(r_obs,r_initial):
    # Finds how much the expected value of the best path changes
    best_action_dir = np.argmax(r_initial)
    best_action_dir_obs = np.argmax(r_obs)
    r_initial_best = r_initial[best_action_dir]
    r_obs = r_obs[best_action_dir]
    best_path_impact = abs(r_obs-r_initial_best)
    change_dir = 0
    if best_action_dir!=best_action_dir_obs:
        change_dir = 1
    return best_path_impact, change_dir

def current_path_norm(r_obs,r_initial,player_action):
    # Finds how much the expected value of the current path changes
    r_i_player_dir = r_initial[player_action]
    r_o_player_dir = r_obs[player_action]
    current_path_impact = abs(r_o_player_dir-r_i_player_dir)
    return current_path_impact

def infomativeness_of_observations(current_state,observations,MDP_simulations,
    num_actions,MDP_reward_model,file_i,file_cum,row_start,data):

    # Only include observations from drones
    obs_include = []
    for obs in observations:
        if obs[2]==0.5:
            obs_include.append(obs)
            # break


    if len(obs_include)!=0:

        # Obtain initial rewards
        # Fill a markov decision process and get reward for the next step
        action_rewards_initial, MDP_i = run_MDP(current_state,MDP_simulations,num_actions,MDP_reward_model)

        # print('Action Costs Initial: '+str(action_rewards_initial))
        # plot_MDP_in_environment(MDP_i, 50)

        # Get the next action the player will take
        trial_time_current_iter = current_state.game_time_data
        _, player_action, _ = data.update_data_state(trial_time_current_iter)

        # Find relative informativeness of observations
        i_obs = 0

        # Iterate backwards through the observations to get most recent info
        id_found = np.zeros(6)
        for i in range(len(obs_include)-1,-1,-1):
            obs = obs_include[i]
            # Has the objectid already been observed
            if id_found[obs[1]]==0:
                # Only include observations from drones
                if obs[2]==0.5:

                    # The agent has been observed...how useful is it??
                    state_1obs = copy.deepcopy(current_state)

                    # Update State with new info for next iteration
                    state_1obs.update_state_with_observations([obs])

                    # Fill a markov decision process and get reward for the next step
                    reward_after_observation, MDP_i = run_MDP(state_1obs,MDP_simulations,num_actions,MDP_reward_model)

                    # print('Action Costs After Observation '+str(i_obs)+': '+str(reward_after_observation))

                    # kl[i_obs] = kl_divergence(reward_after_observation,action_rewards_initial)
                    norm_i = l2_norm(reward_after_observation,action_rewards_initial)
                    norm_bestpath_i, change_dir_i = best_path_norm(reward_after_observation,action_rewards_initial)
                    norm_userpath_i = current_path_norm(reward_after_observation,action_rewards_initial,player_action)

                    row = [trial_time_current_iter, change_dir_i, norm_i, norm_bestpath_i, norm_userpath_i]
                    with open(file_i, 'a') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow(row_start + row)

                    # print('Metrics: ',norm[i_obs])
                    # plot_MDP_in_environment(MDP_i, 50)
                    # plt.show()

                    i_obs += 1

        # Get cummalative benefit of observations
        if i_obs==1:
            with open(file_cum, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(row_start + row)
            # print('Only one observation', i_obs, obs_include)

        else:
            # How useful were all observations cummlatively
            # print('Cummulative update')
            # Update State with new info for next iteration
            current_state.update_state_with_observations(obs_include)
            # done_bool, state_all_obs = update_current_state_with_data(current_state.game_time_data,current_state,state_all_obs,obs_include,1,True)

            # Fill a markov decision process and get reward for the next step
            reward_after_observation, MDP_i = run_MDP(current_state,MDP_simulations,num_actions,MDP_reward_model)
            # print('Action Costs After All Observations: '+str(reward_after_observation))

            norm_i = l2_norm(reward_after_observation,action_rewards_initial)
            norm_bestpath_i, change_dir_i = best_path_norm(reward_after_observation,action_rewards_initial)
            norm_userpath_i = current_path_norm(reward_after_observation,action_rewards_initial,player_action)

            row = [trial_time_current_iter, change_dir_i, norm_i, norm_bestpath_i, norm_userpath_i]
            with open(file_cum, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(row_start + row)

    return True
