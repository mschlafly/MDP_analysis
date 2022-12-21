from env_utils import position
import numpy as np
import random
import copy

class state:
    def __init__(self, trial_time, action, player, adv_list, treasure, environment):
        self.player = player
        self.adversaries = adv_list
        self.treasure = treasure
        self.environment = environment
        self.game_time_data = trial_time # game time from real data

        # For implementations where the locations on the adversaries are only partially observable
        self.partially_observable = False

        in_intersection, intersection_ind = environment.check_person_in_intersection(self.player)
        if in_intersection:
            self.intersection_current = intersection_ind
        else:
            self.intersection_current = 100

        # Start with 0 treasures and lost_lives
        for adv in self.adversaries:
            adv.caught_player = 0
        self.include_treasure = True

        self.player_rate = 4
        self.adv_rate = 3
        self.adversary_moving_rate = (1/.42) # seconds per block
        self.time_include_adv = self.adversary_moving_rate * 10

    # This function simulates the game for a particular player action until the
    # player has reached the next intersection
    def simulate(self, action, firstsim=False):
        # action indicates the turn the player is taking at the current intersection

        # Move forward current observations to simulation time
        if firstsim:
            # Loop through adversaries in adversary_list, bringing them to current time
            for adv in self.adversaries:
                if self.partially_observable:
                    # print([adv.include_probability,1-adv.include_probability])
                    # lspaoisjfp

                    include_bool = np.random.choice([1,0],p=[adv.include_probability,1-adv.include_probability])
                    adv.include = include_bool
                    # adv.include = True
                    # print('include_bool',include_bool)
                    if include_bool:
                        # print(adv.time_observed,adv.sim_time,self.game_time_data)
                        adv.sim_time += self.adversary_moving_rate
                        while adv.sim_time<self.game_time_data:
                            adv.update(self.environment,self.player)
                            adv.sim_time += self.adversary_moving_rate

                        if (adv.sim_time-adv.time_observed)>self.time_include_adv:
                            # print('setting include to false',adv.adv_num)
                            # print(adv.time_observed,adv.sim_time)
                            adv.include = False

                            # print(adv.time_observed,adv.sim_time,self.game_time_data)

                else:
                    adv.include = True # just to make sure all adversaries are included at the beginning
                adv.caught_player = 0 # just in case a life was lost

        in_intersection = False
        while not in_intersection:
            player_steps = 0
            adversary_steps = 0
            while (in_intersection==False) and (player_steps<self.player_rate or adversary_steps<self.adv_rate):

                # Move player/agents
                if player_steps<self.player_rate:
                    edge_of_the_world, new_action = self.move_player(action)
                    if edge_of_the_world:
                        action = new_action
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
                            if self.partially_observable:
                                # Stop including the adversary if it too long after it has been spotted
                                adv.sim_time += self.adversary_moving_rate
                                if (adv.sim_time-adv.time_observed)>self.time_include_adv:
                                    # print('setting include to false',adv.adv_num)
                                    # print(adv.time_observed,adv.sim_time)
                                    adv.include = False

                # Check to see if any of the adversaries see the player
                for adv in self.adversaries:
                    if adv.include:
                        isfound = self.environment.check_sight(adv.pos, self.player, 'sim', action=adv.action)
                        if isfound:
                            adv.is_chasing = True
                            adv.chase = 0

                # Check to see if the player will see any of the adversaries, as this
                # will impact the player's ability to make good decisions in the future
                # The player can tell the direction of the adversary and whether it is chasing
                if self.partially_observable:
                    for adv in self.adversaries:
                        if adv.include:
                            isfound = self.environment.check_sight(self.player, adv.pos, 'sim', action=action, field_of_view=np.pi/1.5)
                            if isfound:
                                # if adv.adversarial:
                                adv.probability_observed = 1
                                adv.time_observed = adv.sim_time
                                # else:
                                #     adv.include = False

                # Did the player catch the treasure?
                isfound, dist_to_treasure = self.is_treasure_found()
                if isfound:
                    self.include_treasure = False

        self.intersection_current = intersection_ind
        lost_lives = 0
        for adv in self.adversaries:
            lost_lives += adv.caught_player
        return lost_lives, dist_to_treasure

    def update_state_with_observations(self,observations):
        # observations is a list of individual observations in format:
        # [game_time, agent_id, probability_observed, pos_x, pos_y, theta, chasing_bool]

        # add new adversaries based on observations and purge existing adversaries
        new_adversary_list = []
        for adv in self.adversaries:
            if self.game_time_data-adv.time_observed < self.time_include_adv:
                new_adversary_list.append(adv)
        for obs in observations:
            # If the agent has already been observed, update the existing info
            include_prob=obs[2]
            pop_i = []
            for i in range(len(new_adversary_list)):
                if obs[1] == new_adversary_list[i].adv_num:
                    if new_adversary_list[i].include_probability==1:
                        include_prob = 1
                    pop_i.append(i)
            if len(new_adversary_list)>0:
                for i in range(len(pop_i)-1,-1,-1):
                    new_adversary_list.pop(i)

            # if not already_exists:
            if obs[1]-1<3:
                new_adversary_list.append(adversary_state(obs[1],
                        obs[3],obs[4],obs[5],adversarial=True,
                        chasing_bool=obs[6],include_probability=include_prob,
                        time_observed=obs[0]))
            else:
                new_adversary_list.append(adversary_state(obs[1],
                        obs[3],obs[4],obs[5],adversarial=False,
                        chasing_bool=obs[6],include_probability=include_prob,
                        time_observed=obs[0]))
        self.adversaries = copy.deepcopy(new_adversary_list)
        for adv in self.adversaries:
            adv.caught_player = 0

    # Move the player one grid space, specified by self.action; also make sure the player doesn't fall off the grid
    def move_player(self, action):

        # Change the person's direction if they are about to fall off the edge of the world
        edge_of_the_world, new_action = self.environment.check_edge(self.player)
        if edge_of_the_world:
            action = new_action
            self.intersection_current = 100 # allow the person to return to the same intersection

        # Move the player
        if action==0:
            self.player.y += 1
        elif action==1:
            self.player.x += 1
        elif action==2:
            self.player.y -= 1
        elif action==3:
            self.player.x -= 1
        return edge_of_the_world, action

    # # used in plotting---what is happening check later!
    # def move_player_temp(self):
    #
    #     # Change the person's direction if they are about to fall off the edge of the world
    #     edge_of_the_world, new_action = self.environment.check_edge(self.player)
    #     if edge_of_the_world:
    #         self.action = new_action
    #         self.intersection_current = 100 # allow the person to return to the same intersection
    #
    #     # Move the player
    #     if self.action==0:
    #         self.player.y += .5
    #     elif self.action==1:
    #         self.player.x += .5
    #     elif self.action==2:
    #         self.player.y -= .5
    #     elif self.action==3:
    #         self.player.x -= .5
    #     return edge_of_the_world

    def is_treasure_found(self):
        dist = np.sqrt(((self.treasure.x - self.player.x)**2) + ((self.treasure.y - self.player.y)**2))
        if dist < 2:
            return True, dist
        else:
            return False, dist

class adversary_state:

    def __init__(self, adv_num, x_pos, z_pos, action, adversarial=True,
            chasing_bool=False, include_probability=1, time_observed=0):
        self.adv_num = adv_num # may not be necessary
        self.pos = position(x_pos,z_pos)
        self.action = action
        self.chase = 0
        self.is_chasing = chasing_bool
        self.intersection_current = 100
        self.caught_player = 0

        # behavior parameters
        self.max_distance_chase = 10
        self.distance_to_loose_life = 2
        self.include = True

        # POMDP parameters
        # self.adversarial = adversarial
        self.include_probability = include_probability
        self.time_observed = time_observed
        self.sim_time = time_observed

    # simulate adversary forward one unit and update the state value if necessary
    def update(self, environment, player):
        # check if the adversary is in a new intersection
        in_intersection, intersection_ind = environment.check_person_in_intersection(self.pos)
        if intersection_ind==self.intersection_current:
            in_intersection = False

        if self.is_chasing:
            if self.chase < self.max_distance_chase:
                dist_to_player = self.nextgoalgrid(environment,player,chase=True)
                self.move_agent(environment)
                self.chase += 1
                distance_to_loose_life = 2
                if dist_to_player < distance_to_loose_life:
                    self.caught_player += 1
                    self.chasing = False
                    self.include = False
            else:
                self.chasing = False

        # Otherwise, model the adversary's actions as random (straight,right,left)
        else:
            # If it is not, keep moving in current direction
            if not in_intersection:
                self.move_agent(environment)

            # Otherwise, if in intersection, randomly chose a turn to take
            else:
                action_uturn = self.get_uturn_action(self.action)
                action_options = []
                for i in range(4):
                    if i!=action_uturn:
                        action_options.append(i)
                self.action = random.choice(action_options)
                self.move_agent(environment)

        if in_intersection:
            self.intersection_current = intersection_ind

    # Find the next grid position for the adversary to be closer to the player
    def nextgoalgrid(self,environment,player,chase=True):
        min_distance = 100000
        goal_x_options = [ self.pos.x + 1, self.pos.x, self.pos.x - 1, self.pos.x ]
        goal_z_options = [ self.pos.y, self.pos.y + 1, self.pos.y, self.pos.y - 1 ]

        # Loop through possible grid locations, chosing the one that is closest to the player
        for i in range(4):
            isonbuilding = self.checkposition(goal_x_options[i], goal_z_options[i], environment)
            if isonbuilding==False:
                distance_temp = np.sqrt(((goal_x_options[i] - player.x)**2) + ((goal_z_options[i] - player.y)**2))
                if min_distance > distance_temp:
                    action_i = i
                    min_distance = distance_temp
        actions = [1,0,3,2] # correspond to goal options; E-N-W-S
        if min_distance == 100000:
            self.choose_random_possible_action(environment)
            min_distance = np.sqrt(((goal_x_options[self.action] - player.x)**2) + ((goal_z_options[self.action] - player.y)**2))
        else:
            self.action = actions[action_i]
        return min_distance

    def checkposition(self, x, z, environment):
        isonbuilding = False
        x = int(np.floor(x))
        z = int(np.floor(z))
        if x > 29: x = 29;
        if z > 29: z = 29;
        if x < 0: x = 0;
        if z < 0: z = 0;
        if environment.building_array[x,z]:
            isonbuilding = True
        return isonbuilding

    # Move the player one grid space, specified by self.action; also make sure the player doesn't fall off the grid
    def move_agent(self, environment, check_on_building=True):

        # Change the person's direction if they are about to fall off the edge of the world
        edge_of_the_world, new_action = environment.check_edge(self.pos)
        if edge_of_the_world:
            self.action = new_action
            self.intersection_current = 100 # allow the person to return to the same intersection

        # Move the player
        if self.action==0:
            self.pos.y += 1
            # if in building, chose random action instead
            if check_on_building:
                isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
                if isonbuilding:
                    self.pos.y -= 1
                    self.choose_random_possible_action(environment)
        elif self.action==1:
            self.pos.x += 1
            # # if in building, chose random action instead
            if check_on_building:
                isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
                if isonbuilding:
                    self.pos.y -= 1
                    self.choose_random_possible_action(environment)
        elif self.action==2:
            self.pos.y -= 1
            # if in building, chose random action instead
            if check_on_building:
                isonbuilding = self.checkposition(self.pos.x, self.pos.y, environment)
                if isonbuilding:
                    self.pos.y -= 1
                    self.choose_random_possible_action(environment)
        elif self.action==3:
            self.pos.x -= 1
            # if in building, chose random action instead
            if check_on_building:
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
            self.action = random.choice(actions)

        # Otherwise, chose randomly from the possible actions
        else:
            self.action = random.choice(possible_actions)

        self.move_agent(environment,check_on_building=False)

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
