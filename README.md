# "Collaborative Robot Augment Human Cognition" Optimal Agent Source Code

This repo determines the optimal agent's actions based on played back experimental data. Metrics based on the optimal agent's actions are compiled under /raw_data in a format that can be copied over to the darpa_dataanalysis github repo.

## Analyses Performed

main.py can perform 4 analyses:

* Validation that model correctly captures the probability of a lost life. This is the default setting---all information is available to the optimal agent and the Hamilton-Jacobi-Bellman equation uses the argmax function. For the following two analyses, the Hamilton-Jacobi-Bellman equation uses the mean function to determine expected reward.
* Player decision analysis where the player's decisions are compared to the optimal agent. Set POMDP_d=True.
* Analysis of the utility of observations to the optimal agent. Set POMDP_obs=True.
* Obtains the number of person observations by drones

## System Requirements

* Python 3.8.10
* multiprocessing package for multithreading
Otherwise, since the code that models how the player's actions influence the environment and builds the Markov Decision Process is contained in this repo, there are few other required packages. To name a few, numpy, pandas, matplotlib, copy, csv, time

## Scripts

- main.py loops through all of the trials, creating and interpreting Markov decision processes as needed, and saving results into csv filed within /raw_data.
- state.py holds a the state class that holds what is known about the player/game state and forward simulates the state.
- main_utils.py contains functions used by main.py
- read_data.py reads csvs that playback the real-time game conditions and provides and updated game state for the MDP
- MDP_class.py builds and populates a MDP for a given state, then determines the expected reward for each turn by updating the Hamilton-Jacobi-Bellman equation. The class defines how one locates itself in the tree and the reward function.
- env_utils.py contains function about how the environment is structured, where building are located, and whether one agent can see another at any point in time
- n_observations.py loops through trials and outputs results in /raw_data/raw_data_n_observations.csv


Helper Functions
- agent_speeds.py determined how fast the adversaries moved for making a more accurate simulated model of the environment
- plot_branching_intersections.py generates Figure 1B from the associated paper using human trial data
- path_figure.py is used to generate the cost of each action for Figure 1A of the paper
- player_path_plot.py plots the path of the player relative to an observed or unobserved adversary for the supplementary material
