from state import state
from env_utils import position, environment
from state import adversary_state
import pandas as pd
import copy
import numpy as np
import random

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'
    """
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

class trial_data:

    def __init__(self, parent_dir, sub, con, env, print=False):
        self.print = print
        self.game_score_unofficial = 3*8
        self.game_time_score_change = 0

        # Read data files
        if sub < 10:
            subID = '0' + str(sub)
        else:
            subID = str(sub)
        environments = ['low', 'high']
        control = ['none', 'waypoint',
                   'directergodic', 'sharedergodic', 'autoergodic']
        trialInfo = subID + '_' + control[con] + '_' + environments[env]
        DIR = parent_dir+'Sub'+subID+'/'+trialInfo+'_'

        try:
            self.player_data = pd.read_csv(DIR+'player.csv')
            self.treasure_data = pd.read_csv(DIR+'treasure.csv')
            # self.objects_data = pd.read_csv(DIR+'objects.csv')
            self.adv0_data = pd.read_csv(DIR+'adv0.csv')
            self.adv1_data = pd.read_csv(DIR+'adv1.csv')
            self.adv2_data = pd.read_csv(DIR+'adv2.csv')
            self.obs_data = pd.read_csv(DIR+'objects.csv')
            self.data_error = False


            self.player_row = self.player_data.index[self.player_data['Time']<=10].tolist()[0]
            self.adv0_row = self.adv0_data.index[self.adv0_data['Time']<=10].tolist()[0]
            self.adv1_row = self.adv1_data.index[self.adv1_data['Time']<=10].tolist()[0]
            self.adv2_row = self.adv2_data.index[self.adv2_data['Time']<=10].tolist()[0]
            self.treasure_row = self.treasure_data.index[self.treasure_data['Time']<=10].tolist()[0]
        except:
            self.data_error = True

        #######################################################################
        # Initialize game state
        #######################################################################
        if self.data_error==False:
            # Player
            player = position(self.player_data['x'].iat[0],self.player_data['y'].iat[0])
            player_theta = self.player_data['theta'].iat[0]
            player_action = self.theta_to_action(np.rad2deg(player_theta))
            self.player_prev_position = copy.deepcopy(player) # the player's position at the previous intersection

            # Adversaries
            adv_list = []
            action = self.theta_to_action(self.adv0_data['theta'].iat[0])
            adv0 = adversary_state(0, self.adv0_data['x'].iat[0], self.adv0_data['y'].iat[0],
                                    action, chasing_bool=False)
            action = self.theta_to_action(self.adv1_data['theta'].iat[0])
            adv1 = adversary_state(0, self.adv1_data['x'].iat[0], self.adv1_data['y'].iat[0],
                                    action, chasing_bool=False)
            action = self.theta_to_action(self.adv2_data['theta'].iat[0])
            adv2 = adversary_state(0, self.adv2_data['x'].iat[0], self.adv2_data['y'].iat[0],
                                    action, chasing_bool=False)
            adv_list = [adv0, adv1, adv2]
            self.adv_prev_position = [copy.deepcopy(adv0.pos),copy.deepcopy(adv1.pos),copy.deepcopy(adv2.pos)]
            self.adv_prev_position_5sec = [copy.deepcopy(adv0.pos),copy.deepcopy(adv1.pos),copy.deepcopy(adv2.pos)]

            # Treasure
            treasure = position(self.treasure_data['x'].iat[0], self.treasure_data['y'].iat[0])

            trial_time = 0
            environ = environment(env)
            self.state = state(trial_time, player_action, player, adv_list, treasure, environ)

    # maybe delete
    def theta_to_action(self, theta):
        while theta<0:
            theta += 360
        while theta>360:
            theta -= 360
        if theta<45 or theta>(360-45):
            action = 0
        elif theta>45 and theta<135:
            action = 1
        elif theta>135 and theta<225:
            action = 2
        else:
            action = 3
        return action

    # Move forward through the data to obtain
    def update_data_state(self,starting_time):

        time = starting_time
        in_intersection = False
        observations = []
        step_time = True
        done_getting_observations = True
        while not in_intersection:

            if step_time and done_getting_observations:
                time += 1 # move one second forward in time
                done_getting_observations = False
            step_time = True

            #######################################################################
            # Update the position of player/agents/treasure
            #######################################################################
            data_time = self.player_data['Time'].iat[self.player_row+1]
            if data_time <= time: # only update if there are rows timestamped in the next second
                self.player_row += 1
                player_prev_position_i = copy.deepcopy(self.state.player)
                self.state.player.x = self.player_data['x'].iat[self.player_row]
                self.state.player.y = self.player_data['y'].iat[self.player_row]
                step_time = False

            data_time = self.adv0_data['Time'].iat[self.adv0_row+1]
            if data_time <= time: # only update if there are rows timestamped in the next second
                self.adv0_row += 1
                self.adv_prev_position[0] = copy.deepcopy(self.state.adversaries[0].pos)
                self.state.adversaries[0].pos.x = self.adv0_data['x'].iat[self.adv0_row]
                self.state.adversaries[0].pos.y = self.adv0_data['y'].iat[self.adv0_row]
                step_time = False

            data_time = self.adv1_data['Time'].iat[self.adv1_row+1]
            if data_time <= time: # only update if there are rows timestamped in the next second
                self.adv1_row += 1
                self.adv_prev_position[1] = copy.deepcopy(self.state.adversaries[1].pos)
                self.state.adversaries[1].pos.x = self.adv1_data['x'].iat[self.adv1_row]
                self.state.adversaries[1].pos.x = self.adv1_data['y'].iat[self.adv1_row]
                step_time = False

            data_time = self.adv2_data['Time'].iat[self.adv2_row+1]
            if data_time <= time: # only update if there are rows timestamped in the next second
                self.adv2_row += 1
                self.adv_prev_position[2] = copy.deepcopy(self.state.adversaries[2].pos)
                self.state.adversaries[2].pos.x = self.adv2_data['x'].iat[self.adv2_row]
                self.state.adversaries[2].pos.x = self.adv2_data['y'].iat[self.adv2_row]
                step_time = False

            data_time = self.treasure_data['Time'].iat[self.treasure_row+1]
            if data_time <= time: # only update if there are rows timestamped in the next second
                self.treasure_row += 1
                treas_prex_x = self.state.treasure.x
                treas_prex_y = self.state.treasure.y
                self.state.treasure.x = self.treasure_data['x'].iat[self.treasure_row]
                self.state.treasure.y = self.treasure_data['y'].iat[self.treasure_row]
                if self.state.treasure.x!=treas_prex_x and self.state.treasure.y!=treas_prex_y:
                    self.game_score_unofficial += 1
                    self.game_time_score_change = time
                step_time = False

            # Make list of found objects
            # observations is a list of individual observations in format:
            # [game_time, agent_id, probability_observed, pos_x, pos_y, action, chasing_bool, ignore]
            if step_time: # if the adveraries and players' positions are no longer being updated
                df_time = self.obs_data[self.obs_data['Time']==time]
                if len(df_time)>1:
                    for id in range(1,6+1):
                        df_id_time = df_time[df_time['id']==id]
                        if len(df_id_time)>1:
                            obj_pos_prev = position(df_id_time['x'].iat[0],df_id_time['y'].iat[0])
                            obj_pos = position(df_id_time['x'].iat[-1],df_id_time['y'].iat[-1])
                            vec_dir = [obj_pos.x-obj_pos_prev.x,obj_pos.y-obj_pos_prev.y]
                            zero_vec = [0, 1]
                            if np.linalg.norm(vec_dir)>0:
                                angle = angle_between(vec_dir, zero_vec) # clockwise=positive for us
                                adv_action = self.theta_to_action(np.rad2deg(angle))
                            elif id<4:
                                adv_num = id-1
                                vec_dir = [self.state.adversaries[adv_num].pos.x-self.adv_prev_position[adv_num].x,self.state.adversaries[adv_num].pos.y-self.adv_prev_position[adv_num].y]
                                angle = angle_between(vec_dir, zero_vec) # clockwise=positive for us
                                adv_action = self.theta_to_action(np.rad2deg(angle))
                            else:
                                adv_action = random.choice([0,1,2,3])
                            if obj_pos.x!=0 and obj_pos.y!=0:
                                if id<4: # if adversary
                                    obs_i = [time, id-1, .5, obj_pos.x, obj_pos.y,
                                            adv_action, self.state.adversaries[id-1].is_chasing, True]
                                else:
                                    obs_i = [time, id-1, .5, obj_pos.x, obj_pos.y,
                                            adv_action, False, True]
                                observations.append(obs_i)
                done_getting_observations = True

            # Check to see if any of the adversaries see the player and how long it has been chasing the player
            adv_num = 0
            for adv in self.state.adversaries:
                # Has the adversary jumped across the screen after catching player ~or~
                # is the adversary no longer going toward the player
                # Not super accurate, but can ensure we don't accedentially set the adversary as chasing the player
                if (time - starting_time) % 5 == 0:
                    dist_adversary_moved = np.linalg.norm([adv.pos.x-self.adv_prev_position[adv_num].x,adv.pos.y-self.adv_prev_position[adv_num].y])
                    dist_adv_to_player = np.linalg.norm([self.adv_prev_position_5sec[adv_num].x-self.state.player.x,self.adv_prev_position_5sec[adv_num].y-self.state.player.y])
                    dist_adv_to_player_prev = np.linalg.norm([adv.pos.x-self.state.player.x,adv.pos.y-self.state.player.y])
                    # if (dist_adversary_moved > 5) or (dist_adv_to_player>dist_adv_to_player_prev+1):
                    if (dist_adversary_moved > 5):# or (dist_adv_to_player>dist_adv_to_player_prev+1):
                    # the player can go over 2 blocks in 5sec
                        if self.print:
                            print('\nAdversary '+str(adv_num)+' stops chasing the player.')
                        adv.is_chasing = False
                        adv.chase = 0
                        self.game_score_unofficial -= 3
                        self.game_time_score_change = time
                    self.adv_prev_position_5sec[adv_num] = copy.deepcopy(self.state.adversaries[adv_num].pos)

                # If chasing, update chasing parameter determining how many squares the adversary has chased the player for
                if adv.is_chasing:
                    if adv.chase < adv.max_distance_chase:
                        adv_prev_pos_xpos = int(np.floor(self.adv_prev_position[adv_num].x))
                        adv_prev_pos_ypos = int(np.floor(self.adv_prev_position[adv_num].y))
                        adv_pos_xpos = int(np.floor(adv.pos.x))
                        adv_pos_ypos = int(np.floor(adv.pos.y))
                        if adv_prev_pos_xpos!=adv_pos_xpos or adv_prev_pos_ypos!=adv_pos_ypos:
                            adv.chase += 1
                            if self.print:
                                print('Adversary '+str(adv_num)+' at ('+
                                        str(int(np.floor(adv.pos.x)))+','+str(int(np.floor(adv.pos.y)))+
                                        ') has chased the player '+str(adv.chase)+' blocks')
                    else:
                        adv.is_chasing = False
                        if self.print:
                            print('Adversary '+str(adv_num)+' at ('+
                                    str(int(np.floor(adv.pos.x)))+','+str(int(np.floor(adv.pos.y)))+
                                    ') has stopped chasing the player')

                isfound = self.state.environment.check_sight(adv.pos, self.state.player, 'data', agent_prev_pos=self.adv_prev_position[adv_num])
                if isfound:
                    adv.is_chasing = True
                    adv.chase = 0
                    if self.print:
                        print('Adversary '+str(adv_num)+' at ('+
                                str(int(np.floor(adv.pos.x)))+','+str(int(np.floor(adv.pos.y)))+
                                ') spotted the player')

                adv_num += 1

            # Check to see if the player has seen any of the adversaries to add new observation
            for adv in self.state.adversaries:
                if adv.include:
                    isfound = self.state.environment.check_sight(self.state.player, adv.pos, 'data',
                            agent_prev_pos=player_prev_position_i)
                    if isfound:
                        vec_dir = [adv.pos.x-self.adv_prev_position[adv.adv_num].x,adv.pos.y-self.adv_prev_position[adv.adv_num].y]
                        zero_vec = [0, 1]
                        angle = angle_between(vec_dir, zero_vec) # clockwise=positive for us
                        adv_action = self.theta_to_action(np.rad2deg(angle))
                        obs_i = [time, adv.adv_num, 1, adv.pos.x, adv.pos.y,
                                adv_action, adv.is_chasing, True]
                        observations.append(obs_i)

            # Check if the player is in a new intersection
            in_intersection, intersection_ind = self.state.environment.check_person_in_intersection(self.state.player)
            if intersection_ind==self.state.intersection_current:
                in_intersection = False

        self.state.intersection_current = intersection_ind
        player_vec = [self.state.player.x-self.player_prev_position.x,self.state.player.y-self.player_prev_position.y]
        zero_vec = [0, 1]
        angle = angle_between(player_vec, zero_vec) # clockwise=positive for us
        player_action = self.theta_to_action(np.rad2deg(angle))
        self.player_prev_position = copy.deepcopy(self.state.player)
        self.adv_prev_position_5sec[0] = copy.deepcopy(self.state.adversaries[0].pos)
        self.adv_prev_position_5sec[1] = copy.deepcopy(self.state.adversaries[1].pos)
        self.adv_prev_position_5sec[2] = copy.deepcopy(self.state.adversaries[2].pos)
        self.state.game_time_data = time

        return time, player_action, observations
