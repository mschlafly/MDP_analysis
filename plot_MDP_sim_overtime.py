
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


subject_list = [8]
subject_list = [8, 36, 40]
subject_list = [1, 29]
# for sub_num in range(len(subject_list)):
for sub in subject_list:
    file = "raw_data/raw_data_MDP_parameters_"+str(sub)+".csv"
    df = pd.read_csv(file)


    environments = ['low', 'high']
    control = ['none', 'waypoint',
               'directergodic', 'sharedergodic', 'autoergodic']

# for sub in subject_list:
    for a in range(1,7):
        plt.figure()
        df_plot = df[(df['Subject'] == sub) & (df['Num_A'] == a)]
        for con in range(0, len(control)):
            for env in range(0, len(environments)):
                df_line = df_plot[(df_plot['Control'] == control[con]) & (df_plot['Complexity'] == environments[env])]
                df_line = df_line.sort_values(by=['Num_sim'])
                plt.plot(df_line['Num_sim'].values, df_line['Regret_cum'].values)

        plt.title('Subject '+str(sub)+' Planning '+str(a)+' Actions Into the Future')
        plt.xlabel('Number of Simulations')
        plt.ylabel('Cummulative Regret')
        plt.ylim([0,15])
        plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.pdf')
        plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.png')

    plt.figure()

    legend = []
    for con in range(0, len(control)):
        for env in range(0, len(environments)):
            regret = np.zeros(6)
            i=0
            legend.append(control[con]+' '+environments[env])
            for a in range(1,7):
                df_plot = df[(df['Subject'] == sub) & (df['Num_A'] == a)]
                df_line = df_plot[(df_plot['Control'] == control[con]) &
                            (df_plot['Complexity'] == environments[env]) &
                            # (df_plot['Num_sim'] == 1097)]
                            (df_plot['Num_sim'] == 4915)]
                val = df_line['Regret_cum'].values
                if len(val)>0:
                    regret[i] = val[0]
                i += 1
            plt.plot(np.linspace(1,6,6),regret)
    plt.title('Subject '+str(sub)+' Cummulative Regret for Different Path Lengths')
    plt.xlabel('Path Length')
    plt.ylabel('Cummulative Regret')
    plt.legend(legend)
    plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_pathlength.pdf')
    plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_pathlength.png')


    plt.close('all')
