
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


file = "raw_data/raw_data_POMDP_d_3a_3s.csv"
df = pd.read_csv(file)

max_regret_window = .3

environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

decision_impact = np.linspace(max_regret_window/2,.5,30)

fig, ax =plt.subplots(nrows=1, ncols=1, dpi=150)
colors5 = ['#BA4900','#BA0071','#0071BA','#00BA49','#00BAA6']

for con in range(0, len(control)):
    perc_regret = ['NaN'] * len(decision_impact)
    df_con = df[(df['Control'] == control[con])]

    for d_i in range(len(decision_impact)):
        decision_impact_i = decision_impact[d_i]
        win_upper_bound = decision_impact_i + max_regret_window/2
        win_lower_bound = decision_impact_i - max_regret_window/2
        # num_values_included = []
        for sub in range(1,42):
            df_sub = df_con[(df_con['Subject'] == sub)]
            if len(df_sub)>0:
                df_win = df_sub[(df_sub['Maximum_Regret'] > win_lower_bound) &
                                (df_sub['Maximum_Regret'] < win_upper_bound)]
                # print(df_win)
                if len(df_sub)>0:
                    # num_values_included.append(len(df_sub))
                    regret = df_win['Regret'].values
                    max_regret = df_win['Maximum_Regret'].values
                    percent_regret_all = np.divide(regret,max_regret)
                    # print(percent_regret_all)
                    # print(perc_regret)
                    if perc_regret[d_i]=='NaN':
                        perc_regret[d_i] = np.array(np.mean(percent_regret_all))
                        # print(np.mean(percent_regret_all))
                        # print(perc_regret)
                    else:
                        perc_regret[d_i] = np.append(perc_regret[d_i],np.mean(percent_regret_all))
                        # perc_regret[con].append(np.mean(percent_regret_all))
                        # print(perc_regret)

        # print('The number of samples included for decision impact '+str(decision_impact_i)+
        #         ' is ', num_values_included)


    # Add to figure
    r_mean = np.zeros(len(decision_impact))
    r_std = np.zeros(len(decision_impact))
    for d_i in range(len(decision_impact)):
        r_mean[d_i] = np.mean(perc_regret[d_i])
        r_std[d_i] = np.std(perc_regret[d_i])

    ax.plot(decision_impact,r_mean,linestyle='-',color=colors5[con])
    ax.fill_between(decision_impact,np.add(r_mean,r_std),y2=np.subtract(r_mean,r_std),
            alpha=0.5,color=colors5[con],linewidth=0.0)

plt.show()
