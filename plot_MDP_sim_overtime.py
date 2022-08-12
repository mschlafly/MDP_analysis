
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


subject_list = [36]
file = "raw_data/raw_data_MDP_parameters.csv"
df = pd.read_csv(file)


environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

for sub in subject_list:
    for a in range(1,7):
        plt.figure()
        df_plot = df[(df['Subject'] == sub) & (df['Num_A'] == a)]
        for env in range(0, len(environments)):
            for con in range(0, len(control)):
                df_line = df_plot[(df_plot['Control'] == control[con]) & (df_plot['Complexity'] == environments[env])]
                df_line = df_line.sort_values(by=['Num_sim'])
                plt.plot(df_line['Num_sim'].values, df_line['Regret_cum'].values)

        plt.title('Subject '+str(sub)+' Planning '+str(a)+' Actions Into the Future')
        plt.xlabel('Number of Simulations')
        plt.ylabel('Cummulative Regret')
        plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.pdf')
        plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.png')
    plt.close('all')
