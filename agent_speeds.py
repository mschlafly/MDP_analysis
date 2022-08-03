
import numpy as np
import pandas as pd

minsub = 1
maxsub = 42
MDP_simulations = 300

# Specify specific subjects to skip here.
skipped_subjects = []

environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

readDataDIR = 'raw_data/playback/'

###############################################################################
# Main script
###############################################################################

rates = []
for sub in range(minsub, maxsub+1):
    if sub < 10:
        subID = '0' + str(sub)
    else:
        subID = str(sub)

    # Loop through trials
    for env in range(0, len(environments)):
        for con in range(0, len(control)):
            trialInfo = subID + '_' + control[con] + '_' + environments[env]
            print(trialInfo)
            DIR = readDataDIR+'Sub'+subID+'/'+trialInfo+'_'

            try:
                data = pd.read_csv(DIR+'adv2.csv')
            except:
                print('Unable to read data')
                break
            data_trial = data[data['Time']<300]
            if len(data_trial)>2:
                row = 0
                count_steps = 0

                pos_x = int(np.floor(data_trial['x'].iat[0]))
                pos_y = int(np.floor(data_trial['y'].iat[0]))
                for i in range(1,len(data_trial)):
                    pos_x_prev = pos_x
                    pos_y_prev = pos_y
                    pos_x = int(np.floor(data_trial['x'].iat[i]))
                    pos_y = int(np.floor(data_trial['y'].iat[i]))
                    if pos_x_prev!=pos_x or pos_y_prev!=pos_y:
                        count_steps += 1

                end_time = data_trial['Time'].iat[i]
                rate = count_steps/end_time
                rates.append(rate)
                # print(rate)
print(rates)
print(np.mean(rates))
