
from read_data import trial_data
from MDP_class import MDP
from env_utils import check_turn

# while loop identifying different intersections

sub = 25
trial = 2

# determine the best decision at an intersection

data = trial_data(sub,trial)
current_state = data.find_next_state(0)
MDP_i = MDP(current_state,check_turn)
