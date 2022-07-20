import numpy as np
import copy

class position:
    def __init__(self, x_pos, y_pos):
        self.x = x_pos
        self.y = y_pos

class environment:
    def __init__(self,env):
        # env is either 'high' or 'low'
        self.building_array = self.populate_building_array(env)

        # Define intersection locations and numbers in simplified grid where
            # x, y = int(np.floor(x/2)) , int(np.floor(y/2))
        self.intersections = np.ones((15,15),dtype=int)*-1
        in_x = [1,3,6,8,11,13,
                            1,3,6,8,11,13,
                            1,3,6,8,11,13,
                            1,3,6,8,11,13,
                            1,3,6,8,11,13,
                            1,3,6,8,11,13]
        in_y = [1,1,1,1,1,1,
                            3,3,3,3,3,3,
                            6,6,6,6,6,6,
                            8,8,8,8,8,8,
                            11,11,11,11,11,11,
                            13,13,13,13,13,13]
        in_ind = 0
        for i in range(len(in_x)):
            self.intersections[in_x[i],in_y[i]] = in_ind
            in_ind += 1

    # checks if the person is in an intersection. If so, returns an index for the intersection.
    def check_person_in_intersection(self,player_loc):
        # transform position to simplified grid

        x_pos = int(np.floor(player_loc.x/2))
        y_pos = int(np.floor(player_loc.y/2))
        if x_pos>14:
            x_pos = 14
        elif x_pos<0:
            x_pos = 0
        if y_pos>14:
            y_pos = 14
        elif y_pos<0:
            y_pos = 0
        in_ind = self.intersections[x_pos,y_pos]
        if in_ind==-1:
            in_intersection = False
        else:
            in_intersection = True
        return in_intersection, in_ind

    # Checks whether the player is at the edge of the world. If so, returns a new action to not fall off the world
    def check_edge(self, player_loc):
        edge_of_the_world = False
        new_action = -1
        if player_loc.x<1:
            new_action = 1
            edge_of_the_world = True
        elif player_loc.x>29:
            new_action = 3
            edge_of_the_world = True
        elif player_loc.y<1:
            new_action = 0
            edge_of_the_world = True
        elif player_loc.y>29:
            new_action = 2
            edge_of_the_world = True
        # if edge_of_the_world:
        #     print('player is at the edge of the world')
        return edge_of_the_world, new_action

    def check_turn(self, player_loc, dir):
        return True

    # PUT IN SEPERATE FILE SO IT CAN BE USED BY READ_DATA????
    # check whether the target is within the sight of the agent
    # 3 conditions
    # within 45 deg of the direction the agent is facing
    # within 10 units of target ----- WHAT??
    # no buildings are in the way
    def check_sight(self, agent, target, type, agent_prev_pos=0, action=100):
        # works for simulatied position/actions (type='sim') and real data (type='data')
        # action: set for 'sim' tells you the direction the player is facing
        # agent_prev_pos: set for 'data', needed to get the direction the player is facing

        agent_pos = copy.deepcopy(agent)
        target_pos = copy.deepcopy(target)


        if type=='sim':
            if action == 0:
                vec_agent_facing = [0,-1]
            elif action == 1:
                vec_agent_facing = [-1,0]
            elif action == 2:
                vec_agent_facing = [0,1]
            elif action == 3:
                vec_agent_facing = [-1,0]

            # translate the agent positions to the middle of the box
            agent_pos.x += .5
            agent_pos.y += .5
            target_pos.x += .5
            target_pos.y += .5
        else:
            vec_agent_facing = [agent_pos.x-agent_prev_pos.y, agent_pos.y-agent_prev_pos.y]
        if np.max(vec_agent_facing) > 0:
            vec_agent_facing /= np.linalg.norm(vec_agent_facing)
        else:
            vec_agent_facing = [100, 100]
        vec_agent_to_target = np.array([target_pos.x-agent_pos.x,target_pos.y-agent_pos.y])
        dist_to_target = np.linalg.norm(vec_agent_to_target)
        vec_agent_to_target_norm = vec_agent_to_target/dist_to_target

        # is_facing_target = False
        # is_within_line_of_sight = False
        if_target_seen = False
        # is_path_on_building = False

        dotproduct = vec_agent_facing[0]*vec_agent_to_target_norm[0] + vec_agent_facing[1]*vec_agent_to_target_norm[1]
        if dotproduct < (np.cos(np.pi/4)):  # Can see 45 degrees right and left
            # is_facing_target = True

            if dist_to_target < 10: # line_of_sight = 10

                # is_within_line_of_sight = True
                if_target_seen = True
                num_tests = 50.0

                v2player_step = vec_agent_to_target/num_tests
                prev_position = np.array([agent_pos.x, agent_pos.y])

                i = 0
                is_path_on_building = False
                # Check the length of the vector for buildings; stop if found
                while ((is_path_on_building is False) and (i <= num_tests)):
                    new_position = np.add(prev_position,v2player_step)

                    # Check for buildings only if you have entered a new grid space along the vector.
                    if ((np.floor(new_position[0]) != np.floor(prev_position[0])) or (np.floor(new_position[1]) != np.floor(prev_position[1]))):
                        x_ind = int(np.floor(new_position[0]))
                        y_ind = int(np.floor(new_position[1]))
                        if x_ind > 29:
                            x_ind = 29
                        elif x_ind < 0:
                            x_ind = 0
                        if y_ind > 29:
                            y_ind = 29
                        elif y_ind < 0:
                            y_ind = 0
                        if (self.building_array[x_ind,y_ind]==1):
                            is_path_on_building = True

                    prev_position = new_position
                    i += 1
            else:
                return False
        else:
            return False

        if if_target_seen and (is_path_on_building is False):
            return True
        else:
            return False


    def populate_building_array(self, env):

        bld_x = np.zeros(0, dtype=int)
        bld_y = np.zeros(0, dtype=int)

        # Add small buildings
        bld_x = np.append(bld_x,
                          [0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 1.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 1.2
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 2.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 2.2
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 5.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 5.2
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 8.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 8.2
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 9.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29],  # Row 9.2
                          axis=0)
        bld_y = np.append(bld_y,
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # Row 1.1
                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # Row 1.2
                           4, 4, 4, 4, 4, 4, 4, 4, 4, 4,  # Row 2.1
                           5, 5, 5, 5, 5, 5, 5, 5, 5, 5,  # Row 2.2
                           14, 14, 14, 14, 14, 14, 14, 14, 14, 14,  # Row 5.1
                           15, 15, 15, 15, 15, 15, 15, 15, 15, 15,  # Row 5.1
                           24, 24, 24, 24, 24, 24, 24, 24, 24, 24,  # Row 8.1
                           25, 25, 25, 25, 25, 25, 25, 25, 25, 25,  # Row 8.2
                           28, 28, 28, 28, 28, 28, 28, 28, 28, 28,  # Row 9.1
                           29, 29, 29, 29, 29, 29, 29, 29, 29, 29],  # Row 9.2
                          axis=0)

        # Add horizontal buildings
        bld_x = np.append(bld_x,
                          [8, 9, 10, 11, 18, 19, 20, 21,  # Row 1.1
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 1.2
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 2.1
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 2.2
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 5.1
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 5.2
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 8.1
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 8.2
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 9.1
                           8, 9, 10, 11, 18, 19, 20, 21],  # Row 9.2
                          axis=0)
        bld_y = np.append(bld_y,
                          [0, 0, 0, 0, 0, 0, 0, 0,  # Row 1.1
                           1, 1, 1, 1, 1, 1, 1, 1,  # Row 1.2
                           4, 4, 4, 4, 4, 4, 4, 4,  # Row 2.1
                           5, 5, 5, 5, 5, 5, 5, 5,  # Row 2.2
                           14, 14, 14, 14, 14, 14, 14, 14,  # Row 5.1
                           15, 15, 15, 15, 15, 15, 15, 15,  # Row 5.2
                           24, 24, 24, 24, 24, 24, 24, 24,  # Row 8.1
                           25, 25, 25, 25, 25, 25, 25, 25,  # Row 8.2
                           28, 28, 28, 28, 28, 28, 28, 28,  # Row 9.1
                           29, 29, 29, 29, 29, 29, 29, 29],  # Row 9.2
                          axis=0)

        # Add vertical buildings
        bld_x = np.append(bld_x,
                          [0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 3/4.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 3/4.2
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 3/4.3
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 3/4.4
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 6/7.1
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 6/7.2
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29,  # Row 6/7.3
                           0, 1, 4, 5, 14, 15, 24, 25, 28, 29],  # Row 6/7.4
                          axis=0)
        bld_y = np.append(bld_y,
                          [8, 8, 8, 8, 8, 8, 8, 8, 8, 8,  # Row 3/4.1
                           9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  # Row 3/4.2
                           10, 10, 10, 10, 10, 10, 10, 10, 10, 10,  # Row 3/4.3
                           11, 11, 11, 11, 11, 11, 11, 11, 11, 11,  # Row 3/4.4
                           18, 18, 18, 18, 18, 18, 18, 18, 18, 18,  # Row 6/7.1
                           19, 19, 19, 19, 19, 19, 19, 19, 19, 19,  # Row 6/7.2
                           20, 20, 20, 20, 20, 20, 20, 20, 20, 20,  # Row 6/7.3
                           21, 21, 21, 21, 21, 21, 21, 21, 21, 21],  # Row 6/7.4
                          axis=0)

        # Add large buildings
        bld_x = np.append(bld_x,
                          [8, 9, 10, 11, 18, 19, 20, 21,  # Row 3/4.1
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 3/4.2
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 3/4.3
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 3/4.4
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 6/7.1
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 6/7.2
                           8, 9, 10, 11, 18, 19, 20, 21,  # Row 6/7.3
                           8, 9, 10, 11, 18, 19, 20, 21],  # Row 6/7.4
                          axis=0)
        bld_y = np.append(bld_y,
                          [8, 8, 8, 8, 8, 8, 8, 8,  # Row 3/4.1
                           9, 9, 9, 9, 9, 9, 9, 9,  # Row 3/4.2
                           10, 10, 10, 10, 10, 10, 10, 10,  # Row 3/4.3
                           11, 11, 11, 11, 11, 11, 11, 11,  # Row 3/4.4
                           18, 18, 18, 18, 18, 18, 18, 18,  # Row 6/7.1
                           19, 19, 19, 19, 19, 19, 19, 19,  # Row 6/7.2
                           20, 20, 20, 20, 20, 20, 20, 20,  # Row 6/7.3
                           21, 21, 21, 21, 21, 21, 21, 21],  # Row 6/7.4
                          axis=0)
        num_blds = np.size(bld_x)

        building_array = np.zeros((30, 30),dtype=bool)
        for i in range(num_blds):
            building_array[bld_x[i], bld_y[i]] = 1

        if env == 'low':
            bld_x = np.zeros(0, dtype=int)
            bld_y = np.zeros(0, dtype=int)

            bld_x = np.append(bld_x,
                              [4, 5, 18, 19, 20, 21,  # Row 2.1
                               4, 5, 18, 19, 20, 21,  # Row 2.2
                               8, 9, 10, 11, 24, 25,  # Row 3.1
                               8, 9, 10, 11, 24, 25,  # Row 3.2
                               8, 9, 10, 11, 18, 19, 20, 21,  # Row 4.1
                               8, 9, 10, 11, 18, 19, 20, 21,  # Row 4.2
                               4, 5, 20, 21,  # Row 5.1
                               4, 5, 20, 21,  # Row 5.2
                               8, 9, 10, 11, 24, 25,  # Row 6.1
                               8, 9, 10, 11, 24, 25,  # Row 6.2
                               8, 9, 10, 11, 18, 19,  # Row 7.1
                               8, 9, 10, 11, 18, 19,  # Row 7.2
                               4, 5, 24, 25,  # Row 8.1
                               4, 5, 24, 25],  # Row 8.2)
                              axis=0)
            bld_y = np.append(bld_y,
                              [4, 4, 4, 4, 4, 4,  # Row 2.1
                               5, 5, 5, 5, 5, 5,  # Row 2.2
                               9, 9, 9, 9, 9, 9,  # Row 3.2
                               8, 8, 8, 8, 8, 8,  # Row 3.1
                               10, 10, 10, 10, 10, 10, 10, 10,  # Row 4.1
                               11, 11, 11, 11, 11, 11, 11, 11,  # Row 4.2
                               14, 14, 14, 14,  # Row 5.1
                               15, 15, 15, 15,  # Row 5.2
                               18, 18, 18, 18, 18, 18,  # Row 6.1
                               19, 19, 19, 19, 19, 19,  # Row 6.2
                               20, 20, 20, 20, 20, 20,  # Row 7.1
                               21, 21, 21, 21, 21, 21,  # Row 7.2
                               24, 24, 24, 24,  # Row 8.1
                               25, 25, 25, 25],  # Row 8.2
                              axis=0)

            num_blds = np.size(bld_x)
            for i in range(num_blds):
                building_array[bld_x[i], bld_y[i]] = 0

        return building_array
