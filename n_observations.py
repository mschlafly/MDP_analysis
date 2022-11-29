import csv
import numpy as np
import pandas as pd

###############################################################################
# Parameters
###############################################################################

minsub = 1
maxsub = 42
time_between_observations = 5

###############################################################################
# Set up csv files
###############################################################################

def create_csv(filePath, columns):
    with open(filePath, 'w') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerow(columns)

file = "raw_data/raw_data_n_observations.csv"
columns = ['Subject', 'Control', 'Complexity','N_observations']
create_csv(file, columns)

###############################################################################
# Determine what subjects to include
###############################################################################

# Specify specific subjects to skip here.
# incomplete subjects and novices
skipped_subjects = [2, 3, 4, 5, 6, 7, 10, 12, 16, 23, 30, 31, 33, 38, 39, 42]
skipped_subjects = []

environments = ['low', 'high']
control = ['none', 'waypoint',
           'directergodic', 'sharedergodic', 'autoergodic']

###############################################################################
# Decide  folder where to save the data
###############################################################################

writeDataDIR = 'raw_data/'
readDataDIR = 'raw_data/playback/'


###############################################################################
# Main script
###############################################################################


for sub in range(minsub, maxsub+1):
    found = False
    for i in range(len(skipped_subjects)):
        if sub == skipped_subjects[i]:
            found = True
            continue
    if found is False:
        if sub < 10:
            subID = '0' + str(sub)
        else:
            subID = str(sub)
    else:
        continue

    # Loop through trials
    for env in range(0, len(environments)):
        for con in range(1, len(control)):

            trialInfo = subID + '_' + control[con] + '_' + environments[env]
            print(trialInfo)

            # Import trial data
            DIR = readDataDIR+'Sub'+subID+'/'+trialInfo+'_'
            data_error = False
            try:
                obs_data = pd.read_csv(DIR+'objects.csv')
                obs_data = obs_data[obs_data['Time']<5*60]
            except:
                print('data error')
                data_error = True


            if not data_error:
                # Loop through agents
                count = 0

                for id in range(1,6+1):
                    df_id = obs_data[obs_data['id']==id]
                    if len(df_id)>0:
                        time_prev_observation = df_id['Time'].iat[0]
                        count += 1
                        for obs in range(len(df_id)):
                            if df_id['Time'].iat[obs]>time_prev_observation+time_between_observations:
                                time_prev_observation = df_id['Time'].iat[obs]
                                count += 1
                row = [subID, control[con], environments[env], count]
                with open(file, 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow(row)
