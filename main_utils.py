from MDP_class import MDP
import numpy as np
import copy
from plot_MDP import plot_MDP_in_environment
import matplotlib.pyplot as plt


def run_MDP(current_state,MDP_simulations,num_player_actions,MDP_reward_model):
    # Initialize and fill the MDP, then update rewards using Bellman equation
    MDP_i = MDP(current_state,num_player_actions,MDP_reward_model)
    MDP_i.populate_tree_parallelized(MDP_simulations)
    MDP_i.update_value_tree()
    next_action_reward = MDP_i.values[:4,0]
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

def infomativeness_of_observations(current_state,observations,MDP_simulations,num_actions,MDP_reward_model):

    # determine how many new drone observations pre-intersection
    obs_include = []
    for id in range(6):
        for obs in observations:
            # Only include observations from drones
            if obs[1]==id and obs[2]==0.5:
                obs_include.append(obs)
                break

    if len(obs_include)==0:
        return False, 0, 0
    else:
        # Obtain initial rewards
        # Fill a markov decision process and get reward for the next step
        action_rewards_initial, MDP_i = run_MDP(current_state,MDP_simulations,num_actions,MDP_reward_model)

        # print('Action Costs Initial: '+str(action_rewards_initial))
        # plot_MDP_in_environment(MDP_i, 50)

        # Find relative informativeness of observations
        obs_len = len(obs_include)
        # kl = np.zeros(obs_len)
        norm = np.zeros(obs_len)
        i_obs = 0
        # Iterate backwards through the observations to get most recent info
        for i in range(obs_len-1,-1,-1):
            obs = obs_include[i_obs]
            # print('observation: ',obs)

            # The agent has been observed...how useful is it??
            state_1obs = copy.deepcopy(current_state)

            # Update State with new info for next iteration
            state_1obs.update_state_with_observations([obs])
            # done_bool, state_1obs = update_current_state_with_data(current_state.game_time_data,current_state,state_1obs,[obs],1,True)

            # Fill a markov decision process and get reward for the next step
            reward_after_observation, MDP_i = run_MDP(state_1obs,MDP_simulations,num_actions,MDP_reward_model)

            # print('Action Costs After Observation '+str(i_obs)+': '+str(reward_after_observation))

            # kl[i_obs] = kl_divergence(reward_after_observation,action_rewards_initial)
            norm[i_obs] = l2_norm(reward_after_observation,action_rewards_initial)

            # print('Metrics: ',norm[i_obs])
            # plot_MDP_in_environment(MDP_i, 50)
            # plt.show()

            i_obs += 1

        # Get cummalative benefit of observations
        if len(obs_include)==1:
            # kl_cum = kl
            norm_cum = norm[0]
        else:
            # How useful were all observations cummlatively

            # Update State with new info for next iteration
            current_state.update_state_with_observations(obs_include)
            # done_bool, state_all_obs = update_current_state_with_data(current_state.game_time_data,current_state,state_all_obs,obs_include,1,True)

            # Fill a markov decision process and get reward for the next step
            reward_after_observation, MDP_i = run_MDP(current_state,MDP_simulations,num_actions,MDP_reward_model)
            # print('Action Costs After All Observations: '+str(reward_after_observation))

            # kl_cum = kl_divergence(reward_after_observation,action_rewards_initial)
            norm_cum = l2_norm(reward_after_observation,action_rewards_initial)
            # print('Metrics: ',norm_cum)

    return True, norm, norm_cum
