from env_utils import position
import numpy as np
from numpy.random import choice

class state:
    def __init__(self, action, player, adv_list, treasure, trial_time, environment):
        # adv_list: [adv0, adv1, adv2]
        self.trial_time = trial_time
        self.player = player
        # self.player.x = int(np.floor(self.player.x))
        # self.player.y = int(np.floor(self.player.y))
        self.action = action
        self.adversaries = adv_list
        # self.player.x = int(np.floor(self.player.x))
        # self.player.y = int(np.floor(self.player.y))
        # same rounding here too!
        self.treasure = treasure
        self.environment = environment
        in_intersection, intersection_ind = environment.check_person_in_intersection(self.player)
        if in_intersection:
            self.intersection_current = intersection_ind
        else:
            self.intersection_current = 100

        # Start with 0 tresures and lost_lives
        # self.lost_lives = 0
        for adv in self.adversaries:
            adv.caught_player = 0
        # self.treasures = 0
        self.dist_to_treasure = np.sqrt(((self.treasure.x - self.player.x)**2) + ((self.treasure.y - self.player.y)**2))
        self.include_treasure = True


        self.player_rate = 2
        self.adv_rate = 3

        # self.rate = .5 # speed of player relative to adversary
        # if self.rate<1:
        #     # multiplier = 1/self.rate
        #     self.player_rate = 1
        #     self.adv_rate = int(np.round(1/self.rate))
        # elif self.rate>1:
        #     self.adv_rate = 1
        # self.possible = check_turn(player, action)

    def simulate(self):
        # Start with 0 tresures and lost_lives
        # self.adv0.caught_player = 0
        # found_treasures = 0

        in_intersection = False
        while not in_intersection:
            player_steps = 0
            adversary_steps = 0
            while player_steps<self.player_rate or adversary_steps<self.adv_rate:
                # Check to see if any of the adversaries see the player
                for adv in self.adversaries:
                    isfound = self.environment.check_sight(adv.pos, self.player, 'sim', action=adv.action)
                    if isfound:
                        adv.is_chasing = True
                        adv.chase = 0

                # Check to see if the player will see any of the adversaries, as this
                # will impact the player's ability to make good decisions in the future
                # The player can tell the direction of the adversary and whether it is chasing


                # Did the player catch the treasure?
                isfound = self.is_treasure_found()
                if isfound:
                    self.include_treasure = False
                    # self.treasures += 1
                    # MAYBE NOT NECESSARY! DEPENDS ON HOW FAR FORWARD WE SIMULATE!
                    # place_treasure()

                # Move players/agents
                if player_steps<self.player_rate:
                    self.move_player()
                    player_steps += 1
                    # See if the player has entered an intersection yet
                    in_intersection, intersection_ind = self.environment.check_person_in_intersection(self.player)
                    if intersection_ind==self.intersection_current:
                        in_intersection = False
                if adversary_steps<self.adv_rate:
                    adversary_steps += 1
                    for adv in self.adversaries:
                        if adv.include:
                            adv.update(self.environment,self.player)
                    # print('sim-adv0 new pos', self.adversaries[1].pos.x,self.adversaries[1].pos.y)


        self.intersection_current = intersection_ind
        lost_lives = 0
        for adv in self.adversaries:
            lost_lives += adv.caught_player
        return lost_lives, self.dist_to_treasure


    def move_adv0(self):
        self.adv0.simulate()

    # Move the player one grid space, specified by self.action; also make sure the player doesn't fall off the grid
    def move_player(self):

        # Change the person's direction if they are about to fall off the edge of the world
        edge_of_the_world, new_action = self.environment.check_edge(self.player)
        if edge_of_the_world:
            self.action = new_action
            self.intersection_current = 100 # allow the person to return to the same intersection

        # Move the player
        if self.action==0:
            self.player.y += 1
        elif self.action==1:
            self.player.x += 1
        elif self.action==2:
            self.player.y -= 1
        elif self.action==3:
            self.player.x -= 1
        return edge_of_the_world

    def is_treasure_found(self):
        dist = np.sqrt(((self.treasure.x - self.player.x)**2) + ((self.treasure.y - self.player.y)**2))
        self.dist_to_treasure = dist
        if dist < 2:
            return True
        else:
            return False

    def place_treasure(self):
        self.treasure = position(50,50)

class adversary_state:

    def __init__(self, adv_num, x_pos, z_pos, action, chasing_bool):
        self.adv_num = adv_num
        self.pos = position(x_pos,z_pos)
        # print('initial positions',self.pos.x,self.pos.y)
        self.action = action

        # self.patrol_index = 0
        self.chase = 0
        self.is_chasing = chasing_bool
        # self.returntopatrol = False

        # self.environment
        self.intersection_current = 100

        self.caught_player = 0

        # behavior parameters
        self.max_distance_chase = 10
        self.distance_to_loose_life = 2
        # self.initialize_dist_to_player = 4

        self.include = True

        # self.patrol_x = [2, 2, 2, 3, 3, 3, 4, 5, 6, 6, 6, 6, 6,
        #                   7, 7, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
        #                   16, 16, 16, 17, 17, 17, 18, 19, 20, 21, 22, 22, 22, 22, 22,
        #                   23, 23, 23, 23, 24, 25, 26, 27, 28, 29, 29, 28, 27,
        #                   27, 27, 27, 27, 27, 27, 27, 26, 26, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17,
        #                   17, 17, 17, 17, 16, 16, 16, 16, 15, 14, 13, 13, 13, 13,
        #                   12, 12, 12, 12, 12, 11, 10, 9, 8, 7, 7, 7,
        #                   6, 6, 6, 5, 4, 3, 2, 1, 0, 0, 1, 2, 2, 2, 2]
        # self.patrol_z = [2, 1, 0, 0, 1, 2, 2, 2, 2, 3, 4, 5, 6,
        #                       6, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
        #                       2, 1, 0, 0, 1, 2, 2, 2, 2, 2, 2, 3, 4, 5, 6,
        #                       6, 5, 4, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2,
        #                       3, 4, 5, 6, 7, 8, 9, 9, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
        #                       6, 5, 4, 3, 3, 4, 5, 6, 6, 6, 6, 5, 4, 3,
        #                       3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 8, 9,
        #                       9, 8, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 5, 4, 3]
        # if self.adv_num==1:
        #     for i in range(len(self.patrol_z)):
        #         self.patrol_z += 10
        # elif self.adv_num==2:
        #     for i in range(len(self.patrol_z)):
        #         self.patrol_z += 20

    # simulate adversary forward one unit and update the state value if necessary
    def update(self, environment, player):
        # If the adversary is currently chasing the player

        # print('adv position beginning',self.pos.x,self.pos.y,self.action)
        # print('chasing',self.is_chasing)
        if self.is_chasing:
            # print('chase',self.chase)
            if self.chase < self.max_distance_chase:
                self.action, dist_to_player = self.nextgoalgrid(environment,player,chase=True)
                self.move_agent(environment)
                self.chase += 1
                distance_to_loose_life = 2
                if dist_to_player < distance_to_loose_life:
                    self.caught_player += 1
                    self.chasing = False
                    self.include = False
            else:
                self.chasing = False
                # set chase = 0 when spotted

        # Otherwise, model the adversary's actions as random (straight,right,left)
        else:
            # check if the adversary is in a new intersection
            in_intersection, intersection_ind = environment.check_person_in_intersection(self.pos)
            if intersection_ind==self.intersection_current:
                in_intersection = False

            # If it is not, keep moving in current direction
            if not in_intersection:
                self.move_agent(environment)

            # Otherwise, randomly chose a turn to take
            else:
                action_uturn = self.get_uturn_action(self.action)
                action_options = []
                for i in range(4):
                    if i!=action_uturn:
                        action_options.append(i)
                self.action = choice(action_options)
                self.move_agent(environment)
        # print('adv position end',self.pos.x,self.pos.y)
        # print('chasing',self.is_chasing)

    # Find the next grid position for the adversary to be closer to the player
    def nextgoalgrid(self,environment,player,chase=True):
        # goal_x_temp = self.pos.x
        # goal_z_temp = self.pos.y
        min_distance = 100000
        goal_x_options = [ self.pos.x + 1, self.pos.x, self.pos.x - 1, self.pos.x ]
        goal_z_options = [ self.pos.y, self.pos.y + 1, self.pos.y, self.pos.y - 1 ]
        # print(self.pos.x,self.pos.y)
        # print(goal_x_options)
        # print(goal_z_options)
        # Loop through possible grid locations, chosing the one that is closest to the player
        for i in range(4):
            isonbuilding = self.checkposition(goal_x_options[i], goal_z_options[i], environment)
            # print(isonbuilding)
            if isonbuilding==False:
                distance_temp = np.sqrt(((goal_x_options[i] - player.x)**2) + ((goal_z_options[i] - player.y)**2))
                if min_distance > distance_temp:
                    action_i = i
                    # goal_x_temp = goal_x_options[i]
                    # goal_z_temp = goal_z_options[i]
                    min_distance = distance_temp
        actions = [1,0,3,2] # correspond to goal options; E-N-W-S
        # if min_distance == 100000:
            # print(self.pos.x,self.pos.y)
            # print(player.x,player.y)
            # print(goal_x_options)
            # print(goal_z_options)
        return actions[action_i], min_distance

    def checkposition(self, x, z, environment):
        isonbuilding = False
        x = int(np.floor(x))
        z = int(np.floor(z))
        if x > 29: x = 29;
        if z > 29: z = 29;
        if x < 0: x = 0;
        if z < 0: z = 0;
        # print(x,z)
        if environment.building_array[x,z]:
            isonbuilding = True
        return isonbuilding

    # Move the player one grid space, specified by self.action; also make sure the player doesn't fall off the grid
    def move_agent(self, environment):

        # Change the person's direction if they are about to fall off the edge of the world
        edge_of_the_world, new_action = environment.check_edge(self.pos)
        if edge_of_the_world:
            self.action = new_action
            self.intersection_current = 100 # allow the person to return to the same intersection

        # Move the player
        if self.action==0:
            self.pos.y += 1
            # if in building, chose random action instead
            isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
            if isonbuilding:
                self.pos.y -= 1
                self.choose_random_possible_action(environment)
        elif self.action==1:
            self.pos.x += 1
            # # if in building, chose random action instead
            isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
            if isonbuilding:
                self.pos.y -= 1
                self.choose_random_possible_action(environment)
        elif self.action==2:
            self.pos.y -= 1
            # if in building, chose random action instead
            isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
            if isonbuilding:
                self.pos.y -= 1
                self.choose_random_possible_action(environment)
        elif self.action==3:
            self.pos.x -= 1
            # if in building, chose random action instead
            isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
            if isonbuilding:
                self.pos.y -= 1
                self.choose_random_possible_action(environment)


        return edge_of_the_world

    # the purpose of this function is to handle scenarios where the real data
    # places the player or adversary in the middle of the
    def choose_random_possible_action(self,environment):
        goal_x_options = [ self.pos.x + 1, self.pos.x, self.pos.x - 1, self.pos.x ]
        goal_z_options = [ self.pos.y, self.pos.y + 1, self.pos.y, self.pos.y - 1 ]
        actions = [1,0,3,2] # correspond to goal options; E-N-W-S

        # Loop through possible grid locations, finding which are possible
        possible_actions = []
        for i in range(4):
            isonbuilding = self.checkposition(goal_x_options[i], goal_z_options[i], environment)
            if isonbuilding==False:
                possible_actions.append(actions[i])
        # There is no possible position without a building, so move randomly
        if len(possible_actions)==0:
            self.action = choice(actions)
            # Move the player
            if self.action==0:
                self.pos.y += 1
            elif self.action==1:
                self.pos.x += 1
            elif self.action==2:
                self.pos.y -= 1
            elif self.action==3:
                self.pos.x -= 1
        # Otherwise, chose randomly from the possible actions
        else:
            # self.action = choice(np.array(possible_actions))
            self.action = choice(possible_actions)
            self.move_agent(environment)


    def get_uturn_action(self,action):
        if action==0:
            uturn = 2
        elif action==1:
            uturn = 3
        elif action==2:
            uturn = 0
        elif action==3:
            uturn = 1
        return uturn

    # def initialize_adversary(player):




        # self.chase = self.max_distance_chase
        # self.returntopatrol = False
        #
        # starting_position_okay = False
        # while !starting_position_okay:
        #
        #     # get random int between 0 and len(self.patrol_x)
        #     distance_temp = np.sqrt(((self.patrol_x[self.patrol_index] + 0.5 - player.x)**2) + ((self.patrol_z[self.patrol_index] + 0.5 - player.y)**2))
        #     if (distance_temp > self.initialize_dist_to_player):




        # adv0 = current_state.adv0
        # adv0, caught1 = move_adv0(adv0)
        #
        # if caught1 or caught2 or caught3:
        #     current_state.value -= 3
        #
        # current_state.adv0 = adv0
        # return current_state
