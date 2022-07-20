from state import state
from env_utils import position, environment
from state import adversary_state

class trial_data:

    def __init__(self, sub, trial, env):
        self.env = env
        # read files and save them here



    # Move forward through the data to obtain
    def find_next_state(self,starting_time):

        # find when the person reaches the intersection, then simulate everything until that point updating the adversary info and V as relevant
        # or just keep simulating forward
        # what did Kat do?? time-wise?

        # puts the person in the center of the intersection
        # simulate the adversaries forward by one unit to match the transformation
        x_pos = 6
        y_pos = 6
        player = position(x_pos,y_pos)

        adv_list = []

        # Adversary 0
        x_pos = 12
        z_pos = 5
        action = 0
        adv0 = adversary_state(0, x_pos, z_pos, action, chasing_bool=False)

        # Adversary 1
        x_pos = 12
        z_pos = 26
        action = 3
        adv1 = adversary_state(1, x_pos, z_pos, action, chasing_bool=False)

        # Adversary 2
        x_pos = 26
        z_pos = 12
        action = 2
        adv2 = adversary_state(2, x_pos, z_pos, action, chasing_bool=False)


        adv_list = [adv0, adv1, adv2]

        x_pos = 19
        y_pos = 26
        treasure = position(x_pos,y_pos)
        trial_time = .2
        environ = environment(self.env)
        new_state = state(10, player, adv_list, treasure, trial_time, environ)

        return new_state
