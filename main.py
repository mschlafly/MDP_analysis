
from read_data import trial_data
from MDP_class import MDP
from env_utils import environment
from plot import plot_MDP_in_environment

# while loop identifying different intersections

sub = 25
trial = 2
env = 'low'
# environment = environment(env)


# determine the best decision at an intersection

data = trial_data(sub,trial,env)
current_state = data.find_next_state(0)
MDP_i = MDP(current_state)
# print(MDP_i.state_init.player.x)
# plot_MDP_in_environment(MDP_i)
MDP_i.populate_tree(1000)
# print(MDP_i.state_init.player.x)
MDP_i.update_value_tree()
print(MDP_i.values)
plot_MDP_in_environment(MDP_i)
