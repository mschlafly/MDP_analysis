import numpy as np
import matplotlib.pyplot as plt
import copy
from numpy.random import choice, shuffle
import math

def get_transparency(value):
    value_max = 1
    value_min = -1*3
    transparency = (value-value_min)*((255-0)/(value_max-value_min))
    return int(np.round(transparency))

def get_color(value):
    max_color = [0,0,255,255]
    min_color = [0,255,255,255]
    value_max = 1
    value_min = -1*2
    # r_val = min_color[0]+(value-value_min)*((max_color[0]-min_color[0])/(value_max-value_min))
    g_val = min_color[1]+(value-value_min)*((max_color[1]-min_color[1])/(value_max-value_min))
    # transparency = (value-value_min)*((255-0)/(value_max-value_min))
    # g_val = 150
    # color = [int(np.round(r_val)),int(np.round(g_val)),255,255]
    color = [0,int(np.round(g_val)),255,255]
    return color

def get_transparency_adversary(value):
    value = -value
    value_max = 0
    value_min = -15
    # value_min = -20
    transparency = (value-value_min)*((255-0)/(value_max-value_min))
    return int(np.round(transparency))


def plot_MDP_in_environment(MDP, num_sims, action_list = 0):

    # Initialize grid
    grid = 255*np.ones((15,15,4),dtype=int)

    # Colors and parameters
    player_color = [24, 148, 51, 255]
    adv_color = [240, 240, 24, 255]
    adv_color_chasing = [255, 94, 0, 255]
    treasure_color = [240, 24, 24, 255]
    bld_color = [0, 0, 0, 255]
    path_color = [132, 0, 255, 255]

    # Loop through different paths randomly, adding intersections and values
    # print('Cost of actions',MDP.values[:4,0])
    for sim in range(num_sims):
        # print('Path '+str(sim))
        in_intersection, intersection_ind = MDP.state_init.environment.check_person_in_intersection(MDP.state_init.player)
        if in_intersection:
            intersection_current = intersection_ind
        else:
            intersection_current = 100

        dist_intersection_to_player = 0
        stop_path = False
        for a_i in range(MDP.a):
            if stop_path:
                break
            action = choice([0,1,2,3])
            if action_list!=0:
                action = action_list[a_i]
            if a_i==0:
                system_state = copy.deepcopy(MDP.state_init)

                # set position of the first child state
                row = action; col = 0
                val_previous = MDP.values[row,col]
            else:
                # Get the grid position of the next state
                val_previous = MDP.values[row,col]
                row,col = MDP.node_child(row,col,action)
            # print('Action '+str(action)+' Reward '+str(val_previous))

            in_intersection = False
            first_iteration = True
            while not in_intersection:
                # Make it so only paths moving away from the players current position are plotted
                if first_iteration:
                    first_iteration = False
                    dist_intersection_to_player_prev = np.linalg.norm([system_state.player.x-MDP.state_init.player.x,system_state.player.y-MDP.state_init.player.y])
                    edge_of_the_world, new_action = system_state.move_player(action)
                    if edge_of_the_world:
                        action = new_action

                    if action_list==0:
                        dist_intersection_to_player = np.linalg.norm([system_state.player.x-MDP.state_init.player.x,system_state.player.y-MDP.state_init.player.y])
                        if dist_intersection_to_player<dist_intersection_to_player_prev:
                            stop_path = True
                            break
                else:
                    # Move player
                    edge_of_the_world, new_action = system_state.move_player(action)
                    if edge_of_the_world:
                        action = new_action

                # See if the player has entered an intersection yet
                in_intersection, intersection_ind = system_state.environment.check_person_in_intersection(system_state.player)
                if intersection_ind==intersection_current:
                    in_intersection = False

                    # print previous color
                    path_color[3] = get_transparency(val_previous)
                    path_color = get_color(val_previous)

                    x_pos = int(np.floor(system_state.player.x/2))
                    y_pos = int(np.floor(system_state.player.y/2))
                    grid[y_pos,x_pos,:] = path_color

                elif in_intersection:
                    intersection_current = intersection_ind
                else:
                    # If not, color the appropiate spot with MDP value
                    if math.isnan(MDP.values[row,col]):
                        in_intersection = True
                        stop_path = True
                    else:
                        path_color[3] = get_transparency(MDP.values[row,col])
                        path_color = get_color(MDP.values[row,col])
                        x_pos = int(np.floor(system_state.player.x/2))
                        y_pos = int(np.floor(system_state.player.y/2))
                        if x_pos>14:
                            x_pos = 14
                        elif x_pos<0:
                            x_pos = 0
                        if y_pos>14:
                            y_pos = 14
                        elif y_pos<0:
                            y_pos = 0
                        grid[y_pos,x_pos,:] = path_color


    # Place player, adversary, target, and buildings
    # this is for env='high'
    bld_x = [0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14,
                0,2,4,5,7,9,10,12,14]
    bld_y = [0,0,0,0,0,0,0,0,0,
                2,2,2,2,2,2,2,2,2,
                4,4,4,4,4,4,4,4,4,
                5,5,5,5,5,5,5,5,5,
                7,7,7,7,7,7,7,7,7,
                9,9,9,9,9,9,9,9,9,
                10,10,10,10,10,10,10,10,10,
                12,12,12,12,12,12,12,12,12,
                14,14,14,14,14,14,14,14,14]
    for i in range(len(bld_x)):
        grid[bld_y[i],bld_x[i],:] = bld_color

    for adv in MDP.state_init.adversaries:
        x_pos = int(np.floor(adv.pos.x/2))
        y_pos = int(np.floor(adv.pos.y/2))
        if adv.is_chasing:
            # adv_color_chasing[3] = get_transparency_adversary(MDP.state_init.game_time_data-adv.time_observed)
            grid[y_pos,x_pos,:] = adv_color_chasing
        else:
            # adv_color[3] = get_transparency_adversary(MDP.state_init.game_time_data-adv.time_observed)
            grid[y_pos,x_pos,:] = adv_color

    treasure = MDP.state_init.treasure
    x_pos = int(np.floor(treasure.x/2))
    y_pos = int(np.floor(treasure.y/2))
    grid[y_pos,x_pos,:] = treasure_color

    player = MDP.state_init.player
    x_pos = int(np.floor(player.x/2))
    y_pos = int(np.floor(player.y/2))
    grid[y_pos,x_pos,:] = player_color

    plt.figure()
    grid = np.flip(grid,axis=0)
    plt.imshow(grid, aspect='equal')
    # plt.show()
