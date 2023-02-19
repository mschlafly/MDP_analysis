from env_utils import position, environment
import matplotlib.pyplot as plt
import pandas as pd
import copy
import numpy as np
import random

# MDP imports
from read_data import trial_data
from main_utils import *
from env_utils import environment

###############################################################################
# Parameters
###############################################################################

minsub = 1
maxsub = 42

sample_time = 30
adversary_is_seen = True
if adversary_is_seen:
    time_increment = 10
else:
    time_increment = 100


# MDP parameters
num_actions = 6
# num_actions = 3
num_sims = 10000
# num_sims = 3000
MDP_reward_model = 'mean'
total_lines = 0

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

readDataDIR = 'raw_data/playback/'


###############################################################################
# Functions
###############################################################################

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'
    """
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def get_color(value):
    value = -value
    min_color = [0,0,255,255]
    max_color = [0,225,255,255]
    value_min = 0
    value_max = 1
    # r_val = min_color[0]+(value-value_min)*((max_color[0]-min_color[0])/(value_max-value_min))
    g_val = min_color[1]-(value-value_min)*((max_color[1]-min_color[1])/(value_max-value_min))
    # transparency = (value-value_min)*((255-0)/(value_max-value_min))
    # g_val = 150
    # if r_val>255:
    #     r_val = 255
    if g_val>255:
        g_val = 255
    # color = (r_val/255,g_val/255,1)
    # color = (r_val/255,0,1)
    color = (0,g_val/255,1)
    # color = [0,int(np.round(g_val)),255,255]
    return color

fig, ax =plt.subplots(nrows=1, ncols=1, dpi=150)
colors5 = ['#BA4900','#BA0071','#0071BA','#00BA49','#00BAA6']
color_max_dist = 15
color_min_dist = 5
# min_color_val = 100/255
# fig.title('Participant\'s Path Relative to Detected Adversary')
# plt.xlabel('x')
# plt.ylabel('y')

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
    for env in range(0,2):
        for con in range(1,5):

            trialInfo = subID + '_' + control[con] + '_' + environments[env]
            DIR = readDataDIR+'Sub'+subID+'/'+trialInfo+'_'
            print(trialInfo)

            try:
                player_data = pd.read_csv(DIR+'player.csv')
                obs_data = pd.read_csv(DIR+'objects.csv')

                if not adversary_is_seen:
                    adv0_data = pd.read_csv(DIR+'adv0.csv')
                    adv1_data = pd.read_csv(DIR+'adv1.csv')
                    adv2_data = pd.read_csv(DIR+'adv2.csv')
                data_error = False


                player_row = player_data.index[player_data['Time']<=10].tolist()[0]
            except:
                data_error = True

            # Initialize data object
            data = trial_data(readDataDIR,sub,con,env,print=False)
            if data.data_error:
                data_error = True

            #######################################################################
            # Initialize game state
            #######################################################################
            if data_error==False:

                time = 30
                environ = environment(env)

                trial_running = True
                trial_time = 0

                # Get initial state/observations from data
                trial_time, player_action, observations = data.update_data_state(trial_time)
                current_state = copy.deepcopy(data.state)
                current_state.partially_observable = True
                current_state.update_state_with_observations(observations)

                num_lines = 0
                while trial_running:
                    time += time_increment
                    # print('loop', time)


                    if trial_time<time: # skip samples if the player hasn't moved far since last sample
                        while time>trial_time:
                            # Simulate trial data forward until the player reaches an intersection
                            trial_time, player_action, observations = data.update_data_state(trial_time)
                            continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,True)

                        if adversary_is_seen:
                            # See if any adversaries are spotted
                            df_time = obs_data[obs_data['Time']==time]
                            if len(df_time)>1:
                                for id in range(1,3+1):
                                    df_id_time = df_time[df_time['id']==id]
                                    if len(df_id_time)>1:
                                        # print(df_id_time)
                                        # Get the position and direction of object
                                        obj_pos_prev = position(df_id_time['x'].iat[0],df_id_time['y'].iat[0])
                                        obj_pos = position(df_id_time['x'].iat[-1],df_id_time['y'].iat[-1])
                                        vec_dir = [obj_pos.x-obj_pos_prev.x,obj_pos.y-obj_pos_prev.y]
                                        zero_vec = [0, -1]
                                        # print(np.linalg.norm(vec_dir))
                                        if np.linalg.norm(vec_dir)>0:
                                            angle = -angle_between(vec_dir, zero_vec) # counterclockwise positive

                                            # If spotted, get the player's future trajectory
                                            df_player_traj = player_data[(player_data['Time']>=time) & (player_data['Time']<time+sample_time)]
                                            df_player_traj.sort_values('Time')
                                            # print(df_player_traj)

                                            player_x_rotated = []
                                            player_y_rotated = []

                                            # Find vector to translate first point to the adversary's location (-1 in y)
                                            player_x = player_data['x'].iat[0]
                                            player_y = player_data['y'].iat[0]
                                            # print(obj_pos.x,obj_pos.y)
                                            origin_vec = np.array([[obj_pos.x],
                                                                    [obj_pos.y-1]])
                                            translate_vec = np.array([[origin_vec[0][0] - player_x],
                                                                    [origin_vec[1][0] - player_y]])
                                            # print(translate_vec)
                                            if np.linalg.norm(translate_vec)>color_min_dist and np.linalg.norm(translate_vec)<color_max_dist:
                                                for i in range(0,len(df_player_traj)):
                                                    # player_x = player_data['x'].iat[i]
                                                    # player_y = player_data['y'].iat[i]                                    # print(player_x)
                                                    player_vec = np.array([[player_data['x'].iat[i]],
                                                                            [player_data['y'].iat[i]]])
                                                    # print(player_vec[0][0],player_vec[1][0])

                                                    # Find position relative to the adversary's location
                                                    player_vec = np.add(player_vec,translate_vec)
                                                    # print(player_vec[0][0],player_vec[1][0])

                                                    # Go from global coordinates to local coordinates
                                                    player_vec_local = np.subtract(player_vec,origin_vec)
                                                    # print(player_vec[0][0],player_vec[1][0])

                                                    # print(player_vec)
                                                    # Rotate relative the adversary's angle
                                                    rotation_matrix = np.array([[np.cos(-angle),-np.sin(-angle)],
                                                                                [np.sin(-angle),np.cos(-angle)]])
                                                    player_vec_rotated = np.matmul(rotation_matrix,player_vec_local)

                                                    # Scale so that the distance to the located adversary is 1
                                                    if np.linalg.norm(player_vec)>0:
                                                        player_vec_scaled = np.divide(player_vec_rotated,np.linalg.norm(player_vec))
                                                    else:
                                                        player_vec_scaled = np.array([[0],[0]])

                                                    # Translate 1 downward in y
                                                    player_x_rotated.append(player_vec_scaled[0][0])
                                                    player_y_rotated.append(player_vec_scaled[1][0])

                                                # get next decision regret
                                                next_action_reward, MDP_i = run_MDP(current_state,num_sims,num_actions,MDP_reward_model)
                                                # Simulate trial data forward until the player reaches an intersection
                                                trial_time, player_action, observations = data.update_data_state(trial_time)
                                                continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,True)


                                                player_action_reward = next_action_reward[player_action]
                                                best_action_reward = np.amax(next_action_reward)
                                                regret_i = best_action_reward-player_action_reward
                                                max_regret_possible = best_action_reward - np.amin(next_action_reward)
                                                regret_percent = regret_i / max_regret_possible

                                                color_tuple = get_color(regret_percent)
                                                # color_tuple = get_color(.5)
                                                ax.plot(player_x_rotated,player_y_rotated,linestyle='-',color=color_tuple)
                                                total_lines += 1
                                                # num_lines+=1
                                                # if num_lines>3:
                                                #     trial_running = False
                        else:
                            adv_num_tried = np.zeros(3)
                            while np.sum(adv_num_tried)<3:
                                adv_num = np.random.randint(0,3)
                                for adv in current_state.adversaries:
                                    if adv.adv_num == adv_num:
                                        adv_num_tried[adv_num] = 1
                                        break
                                if adv_num_tried[adv_num]==0:
                                    break
                            if np.sum(adv_num_tried)<3:
                                if adv_num==0:
                                    df_time = adv0_data[(adv0_data['Time']>=time) & (adv0_data['Time']<(time+1))]
                                elif adv_num==1:
                                    df_time = adv1_data[(adv1_data['Time']>=time) & (adv1_data['Time']<(time+1))]
                                else:
                                    df_time = adv2_data[(adv2_data['Time']>=time) & (adv2_data['Time']<(time+1))]

                                # Get the position and direction of object
                                obj_pos_prev = position(df_time['x'].iat[0],df_time['y'].iat[0])
                                obj_pos = position(df_time['x'].iat[-1],df_time['y'].iat[-1])
                                vec_dir = [obj_pos.x-obj_pos_prev.x,obj_pos.y-obj_pos_prev.y]
                                zero_vec = [0, -1]
                                if np.linalg.norm(vec_dir)>0:
                                    angle = -angle_between(vec_dir, zero_vec) # counterclockwise positive

                                    # If spotted, get the player's future trajectory
                                    df_player_traj = player_data[(player_data['Time']>=time) & (player_data['Time']<time+sample_time)]
                                    df_player_traj.sort_values('Time')
                                    # print(df_player_traj)

                                    player_x_rotated = []
                                    player_y_rotated = []

                                    # Find vector to translate first point to the adversary's location (-1 in y)
                                    player_x = player_data['x'].iat[0]
                                    player_y = player_data['y'].iat[0]
                                    # print(obj_pos.x,obj_pos.y)
                                    origin_vec = np.array([[obj_pos.x],
                                                            [obj_pos.y-1]])
                                    translate_vec = np.array([[origin_vec[0][0] - player_x],
                                                            [origin_vec[1][0] - player_y]])
                                    # print(translate_vec)
                                    if np.linalg.norm(translate_vec)>color_min_dist and np.linalg.norm(translate_vec)<color_max_dist:
                                        for i in range(0,len(df_player_traj)):
                                            # player_x = player_data['x'].iat[i]
                                            # player_y = player_data['y'].iat[i]                                    # print(player_x)
                                            player_vec = np.array([[player_data['x'].iat[i]],
                                                                    [player_data['y'].iat[i]]])
                                            # print(player_vec[0][0],player_vec[1][0])

                                            # Find position relative to the adversary's location
                                            player_vec = np.add(player_vec,translate_vec)
                                            # print(player_vec[0][0],player_vec[1][0])

                                            # Go from global coordinates to local coordinates
                                            player_vec_local = np.subtract(player_vec,origin_vec)
                                            # print(player_vec[0][0],player_vec[1][0])

                                            # print(player_vec)
                                            # Rotate relative the adversary's angle
                                            rotation_matrix = np.array([[np.cos(-angle),-np.sin(-angle)],
                                                                        [np.sin(-angle),np.cos(-angle)]])
                                            player_vec_rotated = np.matmul(rotation_matrix,player_vec_local)

                                            # Scale so that the distance to the located adversary is 1
                                            if np.linalg.norm(player_vec)>0:
                                                player_vec_scaled = np.divide(player_vec_rotated,np.linalg.norm(player_vec))
                                            else:
                                                player_vec_scaled = np.array([[0],[0]])

                                            # Translate 1 downward in y
                                            player_x_rotated.append(player_vec_scaled[0][0])
                                            player_y_rotated.append(player_vec_scaled[1][0])

                                        # get next decision regret
                                        next_action_reward, MDP_i = run_MDP(current_state,num_sims,num_actions,MDP_reward_model)
                                        # Simulate trial data forward until the player reaches an intersection
                                        trial_time, player_action, observations = data.update_data_state(trial_time)
                                        continue_bool, current_state = update_current_state_with_data(trial_time,data.state,current_state,observations,sub,True)


                                        player_action_reward = next_action_reward[player_action]
                                        best_action_reward = np.amax(next_action_reward)
                                        regret_i = best_action_reward-player_action_reward
                                        max_regret_possible = best_action_reward - np.amin(next_action_reward)
                                        regret_percent = regret_i / max_regret_possible

                                        color_tuple = get_color(regret_percent)

                                        # color_tuple = get_color(.5)
                                        ax.plot(player_x_rotated,player_y_rotated,linestyle='-',color=color_tuple)
                                        total_lines += 1
                                        num_lines+=1
                                        if num_lines>1:
                                            trial_running = False
                    if sub==17 or sub==18:
                        if time>60*5-45-time_increment-5:
                            trial_running = False
                    if time>60*5-30-time_increment-5:
                        trial_running = False
                    if not continue_bool:
                        break
ax.set_title('Participant\'s Path Relative to Detected Adversary')
ax.set_xlim(-1,1)
ax.set_ylim(-1,1)
ax.set_aspect('equal')
ax.grid(linestyle='-', which='major', axis='both', color='lightgrey',
               alpha=0.5)
print('The total number of trajectories in the plot is '+str(total_lines))
if adversary_is_seen:
    fig.savefig('Plots/player_path_rel2_adversary_seen.png')
    fig.savefig('Plots/player_path_rel2_adversary_seen.pdf')
else:
    fig.savefig('Plots/player_path_rel2_adversary_notseen.png')
    fig.savefig('Plots/player_path_rel2_adversary_notseen.pdf')
plt.show()
