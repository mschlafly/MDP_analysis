import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

Type = 'MDP'

if Type=='MDP':
    subject_list = [20, 8, 36]
elif Type=='POMDP':
    subject_list = [15,24,41]


num_a_in_plot = 10
# if Type=='POMDP':
#     num_a_in_plot = 10

# for sub_num in range(len(subject_list)):
# for sub in subject_list:
if Type=='MDP':
    file = "raw_data/raw_data_MDP_parameters.csv"
elif Type=='POMDP':
    file = "raw_data/raw_data_POMDP_parameters.csv"
df = pd.read_csv(file)


environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

for a in [3,4,5,6,8,10]:
    plt.figure()
    for sub in subject_list:
        df_plot = df[(df['Subject'] == sub) & (df['Num_A'] == a)]
        for con in range(0, len(control)):
            for env in range(0, len(environments)):
                df_line = df_plot[(df_plot['Control'] == control[con]) & (df_plot['Complexity'] == environments[env])]
                df_line = df_line.sort_values(by=['Num_sim'])
                # if Type=='MDP':
                #     plt.plot(df_line['Num_sim'].values, df_line['Regret_cum'].values)
                # elif Type=='POMDP':
                plt.plot(df_line['Num_sim'].values[5:], df_line['Regret'].values[5:])

    plt.title('Planning '+str(a)+' Actions Into the Future')
    plt.xlabel('Number of Simulations')
    if Type=='MDP':
        plt.ylabel('Cummulative Regret')
        plt.ylim([-.05,4])
        plt.savefig('Plots/MDP_param_setting/a'+str(a)+'.pdf')
        plt.savefig('Plots/MDP_param_setting/a'+str(a)+'.png')
        # plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.pdf')
        # plt.savefig('Plots/MDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.png')
    elif Type=='POMDP':
        plt.ylabel('Regret')
        plt.ylim([-.05,2])
        plt.savefig('Plots/POMDP_param_setting/a'+str(a)+'.pdf')
        plt.savefig('Plots/POMDP_param_setting/a'+str(a)+'.png')
        # plt.savefig('Plots/POMDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.pdf')
        # plt.savefig('Plots/POMDP_param_setting/sub'+str(sub)+'_a'+str(a)+'.png')


plt.figure()
legend = []
for sub in subject_list:
    for con in range(0, len(control)):
        for env in range(0, len(environments)):
            regret = []
            i=0
            plot_trial = True
            # legend.append(control[con]+' '+environments[env])
            for a in [3,4,5,6,8,10]:
                df_plot = df[(df['Subject'] == sub) & (df['Num_A'] == a)]
                df_line = df_plot[(df_plot['Control'] == control[con]) &
                            (df_plot['Complexity'] == environments[env])]
                            # (df_plot['Num_sim'] == 1097)]
                            # (df_plot['Num_sim'] >= 4915) &  (df_plot['Num_sim'] <= 4921)]
                            # (df_plot['Num_sim'] >= 13360) &  (df_plot['Num_sim'] <= 13377)]

                df_line = df_line.sort_values(by=['Num_sim'],ascending=False)
                # print(df_line[0])
                # val = df_line['Regret_cum'].values
                # if a<4:
                #     # df_trial =  df_line[(df_line['Num_sim'] == 8103)]
                #     df_trial =  df_line[(df_line['Num_sim'] == 4915)]
                # else:
                #     df_trial =  df_line[(df_line['Num_sim'] >= 28282) & (df_line['Num_sim'] <= 28318)]
                # df_trial =  df_line[(df_line['Num_sim'] >= 28282) & (df_line['Num_sim'] <= 28318)]

                # if Type!='MDP' or sub!=1 or a!=2:
                # if Type=='MDP':
                #     val = df_line['Regret_cum'].values
                # elif Type=='POMDP':
                val = df_line['Regret'].values
                # print(sub,env,con,len(val),val)
                if len(val)>0:
                    regret.append(val[0])
                else:
                    plot_trial = False

                i += 1

            if plot_trial:
                x = [3,4,5,6,8,10]
                # x = np.linspace(1,num_a_in_plot,num_a_in_plot)
                # if Type=='POMDP':
                #     x = np.delete(x,9-1)
                #     regret = np.delete(regret,9-1)
                #     if sub==13 or sub==32:
                #         x = np.delete(x,-1)
                #         x = np.delete(x,-1)
                #         regret = np.delete(regret,-1)
                #         regret = np.delete(regret,-1)

                # regret = np.delete(regret,7-1)
                # x = np.delete(x,7-1)
                # if Type=='MDP' and sub==1:
                #     x = np.delete(x,1)
                #     regret = np.delete(regret,1)
                plt.plot(x,regret)
            # plt.plot([1,2,3,4,5,6,8],regret)
if Type=='MDP':
    # plt.title('Subject '+str(sub)+' Cummulative Regret for Different Path Lengths')
    plt.title('Cummulative Regret for Different Path Lengths')
else:
    plt.title('Percent Regret for Different Path Lengths \n and Sample Intersection')
plt.xlabel('Path Length')
plt.legend(legend)
if Type=='MDP':
    plt.ylabel('Cummulative Regret')
    plt.savefig('Plots/MDP_param_setting/pathlength.pdf')
    plt.savefig('Plots/MDP_param_setting/pathlength.png')
elif Type=='POMDP':
    plt.ylabel('Regret')
    plt.savefig('Plots/POMDP_param_setting/pathlength.pdf')
    plt.savefig('Plots/POMDP_param_setting/pathlength.png')


plt.close('all')
