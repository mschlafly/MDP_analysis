

class state:
    def __init__(self, action, player, adv1, trial_time):
        self.trial_time = trial_time
        self.player = player
        self.action = action
        self.adv1 = adv1

        self.possible = check_turn(player, action)

    def simulate():
        between_intersection = True
        while between_intersection:
            self.move_player()
            self.move_adv1()


            # Simulate the adversaries forward twice to match the 2 unit movement of the player
            child_state = simulate_adversaries(child_state)
            child_state = simulate_adversaries(child_state)

            between_intersection = check_person_in_intersection(person_loc)

        return child_state

    def move_adv1():
        self.adv1.simulate()
        self.adv1.simulate()

    # Find the next grid location in the action specified to move the player
    def move_player():
        if action==0:
            self.player.y += 2
        elif action==1:
            self.player.x += 2
        elif action==2:
            self.player.y -= 2
        elif action==3:
            self.player.x -= 2
        else:
            return False
        return True

class adversary_state:

    def __init__(self, x_pos, y_pos):
        self.pos = position(x_pos,y_pos)

    # simulate all adversaries forward one unit and update the state value if necessary
    def simulate(current_state):
        adv1 = current_state.adv1
        adv1, caught1 = move_adv1(adv1)

        if caught1 or caught2 or caught3:
            current_state.value -= 3

        current_state.adv1 = adv1
        return current_state
