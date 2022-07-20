import numpy as np
import matplotlib.pyplot as plt
import copy
from numpy.random import choice, shuffle
import math

# player_color = [255, 94, 0, 255]
# rgb_array = [[[166, 231, 255, 255],[166, 231, 255, 50]],[[212, 45, 19, 255], [212, 45, 19, 50]]]
#
# # rgb_array = [[255.000, 56.026 + (255 - 56.026) * i / 400, 255 * i / 400] for i in range(400)]
# # rgb_array += [[255 - 255 * i / 600, 255 - 255 * i / 600, 255] for i in range(600)]
# # print(np.array(rgb_array).shape)
# # img = np.array(rgb_array, dtype=int).reshape((1, len(rgb_array), 3))
#
# img = np.array(rgb_array, dtype=int)#.reshape((2, 2, 3))
# plt.imshow(img, aspect='equal')
# plt.show()

def get_transparency(value):
    value_max = 1
    value_min = -2*3
    transparency = (value-value_min)*((255-0)/(value_max-value_min))

    # ((value-value_min)/(value_max-value_min)) + value_min
    # transparency = ((value-value_min)/(value_max-value_min)) + value_min
    return int(np.round(transparency))

def plot_MDP_in_environment(MDP):

    # Initialize grid
    grid = 255*np.ones((15,15,4),dtype=int)


    # Colors and parameters
    player_color = [255, 94, 0, 255]
    adv_color = [240, 240, 24, 255]
    treasure_color = [240, 24, 24, 255]
    bld_color = [0, 0, 0, 150]
    path_color = [132, 0, 255, 255]
    intersection_color = [24, 148, 51, 255]


    # Loop through different paths randomly, adding intersections and values
    num_sims = 50
    print('Cost of actions',MDP.values[:4,0])
    for sim in range(num_sims):
        in_intersection, intersection_ind = MDP.state_init.environment.check_person_in_intersection(MDP.state_init.player)
        # print(in_intersection, intersection_ind)
        if in_intersection:
            intersection_current = intersection_ind
            # print(in_intersection)
        else:
            intersection_current = 100
        stop_path = False
        for a_i in range(MDP.a):
        # for a_i in range(3):
            if stop_path:
                break
            # print('action', a_i)
            action = choice([0,1,2,3])
            if a_i==0:
                system_state = copy.deepcopy(MDP.state_init)

                # set position of the first child state
                row = action; col = 0
            else:
                # Get the grid position of the next state
                row,col = MDP.node_child(row,col,action)
            system_state.action = action


            in_intersection = False
            while not in_intersection:
                # Move player
                system_state.move_player()
                # print("player",system_state.player.x,system_state.player.y)

                # See if the player has entered an intersection yet
                in_intersection, intersection_ind = system_state.environment.check_person_in_intersection(system_state.player)
                # print(in_intersection,intersection_ind)
                if intersection_ind==intersection_current:
                    in_intersection = False
                    # print(in_intersection)

                # Color block
                elif in_intersection:
                    # print('reached intersection')
                    intersection_current = intersection_ind
                    # color intersection
                    x_pos = int(np.floor(system_state.player.x/2))
                    y_pos = int(np.floor(system_state.player.y/2))
                    grid[y_pos,x_pos,:] = intersection_color
                    # continue
                else:
                    # If not, color the appropiate spot with MDP value
                    # print(MDP.values[row,col])
                    # print(MDP.values[row,col])
                    if math.isinf(MDP.values[row,col]):
                        in_intersection = True
                        stop_path = True
                        # print('stopping excecution')
                    else:
                        path_color[3] = get_transparency(MDP.values[row,col])
                        x_pos = int(np.floor(system_state.player.x/2))
                        y_pos = int(np.floor(system_state.player.y/2))
                        # print(path_color)
                        # print('coloring',x_pos,y_pos)
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

    player = MDP.state_init.player
    x_pos = int(np.floor(player.x/2))
    y_pos = int(np.floor(player.y/2))
    # print(player,x_pos,y_pos)
    # x_pos = 3
    # y_pos = 3
    grid[y_pos,x_pos,:] = player_color

    for adv in MDP.state_init.adversaries:
        x_pos = int(np.floor(adv.pos.x/2))
        y_pos = int(np.floor(adv.pos.y/2))
        grid[y_pos,x_pos,:] = adv_color

    treasure = MDP.state_init.treasure
    x_pos = int(np.floor(treasure.x/2))
    y_pos = int(np.floor(treasure.y/2))
    grid[y_pos,x_pos,:] = treasure_color

    grid = np.flip(grid,axis=0)
    plt.imshow(grid, aspect='equal')
    plt.show()
