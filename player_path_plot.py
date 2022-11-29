from env_utils import position, environment
import matplotlib.pyplot as plt
import pandas as pd
import copy
import numpy as np
import random

###############################################################################
# Parameters
###############################################################################

minsub = 1
maxsub = 42

time_increment = 30
sample_time = 30

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
    min_color = [230,0,255,255]
    max_color = [75,0,255,255]
    value_min = 3
    value_max = 30
    r_val = min_color[0]+(value-value_min)*((max_color[0]-min_color[0])/(value_max-value_min))
    # g_val = min_color[1]-(value-value_min)*((max_color[1]-min_color[1])/(value_max-value_min))
    # transparency = (value-value_min)*((255-0)/(value_max-value_min))
    # g_val = 150
    if r_val>255:
        r_val = 255
    # if g_val>255:
    #     g_val = 255
    # color = (r_val/255,g_val/255,1)
    color = (r_val/255,0,1)
    # color = [0,int(np.round(g_val)),255,255]
    return color

fig, ax =plt.subplots(nrows=1, ncols=1, dpi=150)
colors5 = ['#BA4900','#BA0071','#0071BA','#00BA49','#00BAA6']
# color_max_dist = 30
color_min_dist = 3
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

            try:
                player_data = pd.read_csv(DIR+'player.csv')
                obs_data = pd.read_csv(DIR+'objects.csv')
                data_error = False


                player_row = player_data.index[player_data['Time']<=10].tolist()[0]
            except:
                data_error = True

            #######################################################################
            # Initialize game state
            #######################################################################
            if data_error==False:

                time = 0
                environ = environment(env)

                trial_running = True
                while trial_running:
                    time += time_increment
                    # print('loop', time)

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
                                    if np.linalg.norm(translate_vec)>color_min_dist:
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


                                        # color_val = min_color_val + ((np.linalg.norm(translate_vec)-color_min_dist)/(color_max_dist-color_min_dist))*(1-min_color_val)
                                        # if color_val>1:
                                        #     color_val = 1
                                        # if color_val<min_color_val:
                                        #     color_val = min_color_val
                                        #     # print('color too light')
                                        # color_val = 1-color_val
                                        color_tuple = get_color(np.linalg.norm(translate_vec))
                                        ax.plot(player_x_rotated,player_y_rotated,linestyle='-',color=color_tuple)
                    if sub==17 or sub==18:
                        if time>60*5-45-time_increment:
                            trial_running = False
                    if time>60*5-30-time_increment:
                        trial_running = False
ax.set_title('Participant\'s Path Relative to Detected Adversary')
ax.set_xlim(-1,1)
ax.set_ylim(-1,1)
ax.set_aspect('equal')
ax.grid(linestyle='-', which='major', axis='both', color='lightgrey',
               alpha=0.5)
fig.savefig('Plots/player_path_rel2_adversary.pdf')
plt.show()
