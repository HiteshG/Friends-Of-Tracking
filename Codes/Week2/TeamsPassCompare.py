# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 16:41:32 2021

@author: Harry
"""


#Understand the relationship between number of passes and shots
#Compare teams in where they create chance from

# Data Path
path = "C:/Users/Harry/Friends-Of-Tracking/data/"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from FCPython import createPitch
import json

#Function for finding passes before shot - Danger Shots
shot_window = 15    
def in_range(pass_time,start,finish):
        return (True in ((start < pass_time) & (pass_time < finish)).unique())

#Size of the pitch in yards (!!!)
pitchLengthX=120
pitchWidthY=80

#Load the competition file
#Got this by searching 'how do I open json in Python'
with open(path + 'Statsbomb/data/competitions.json') as f:
    competitions = json.load(f)
    
#Womens World Cup 2019 has competition ID 72
competition_id=72

#Load the list of matches for this competition
with open(path + 'Statsbomb/data/matches/'+str(competition_id)+'/30.json') as f:
    matches = json.load(f)

#Get all the teams and match_ids
teams=[]
match_ids=[]
for match in matches:
    if not(match['home_team']['home_team_name'] in teams):
        teams.append(match['home_team']['home_team_name'])
    if not(match['away_team']['away_team_name'] in teams):
        teams.append(match['away_team']['away_team_name'])

    match_ids.append([match['match_id']])

#Collect passes and shots for all players.
passshot_df = pd.DataFrame(columns=['Team','Passes','Shots','Goals','Matches','Danger Passes'])
danger_passes_by=dict()
number_of_matches=dict()

# Loop over matches
for match in matches:
    match_id=match['match_id']
    file_name=str(match_id)+'.json'
    
    # Event data load
    with open(path + 'Statsbomb/data/events/'+file_name) as data_file:
        data = json.load(data_file)
    dfall = pd.json_normalize(data, sep = "_").assign(match_id = file_name[:-5])
    
    print(match['home_team']['home_team_name'] + ' vs ' + match['away_team']['away_team_name'])
    
    #Both team of match
    for theteam in [match['home_team']['home_team_name'],match['away_team']['away_team_name']]:
        team_actions = (dfall['team_name']==theteam)
        df = dfall[team_actions]
        #A dataframe of passes
        passes_match = df.loc[df['type_name'] == 'Pass'].set_index('id')
        #A dataframe of shots
        shots_match = df.loc[df['type_name'] == 'Shot'].set_index('id')

        #Find passes within 15 seconds of a shot, exclude corners.
        shot_times = shots_match['minute']*60+shots_match['second']
        shot_start = shot_times - shot_window
        pass_times = passes_match['minute']*60+passes_match['second']
        pass_to_shot = pass_times.apply(lambda x: in_range(x,shot_start,shot_times))
        iscorner = passes_match['pass_type_name']=='Corner'
        danger_passes=passes_match[np.logical_and(pass_to_shot,np.logical_not(iscorner))]
        
        if theteam in danger_passes_by:
            danger_passes_by[theteam]= danger_passes_by[theteam].append(danger_passes)
            number_of_matches[theteam]=number_of_matches[theteam]+1
        else:
            danger_passes_by[theteam]= danger_passes
            number_of_matches[theteam]=1
            
        if theteam==match['home_team']['home_team_name']:
            goalsscored=match['home_score']
        else:
            goalsscored=match['away_score']
            
        passshot_df = passshot_df.append({
                    "Team": theteam,
                    "Passes": len(passes_match),
                    "Shots": len(shots_match),
                    "Goals": goalsscored,
                    "Danger Passes": len(danger_passes)
                    },ignore_index=True)       

#Plot passes vs. shots. 
fig,ax=plt.subplots(num=1)
ax.plot('Passes','Shots', data=passshot_df, linestyle='none', markersize=4, marker='o', color='grey')
team_of_interest="United States Women's"
# team_of_interest="England Women's"
team_of_interest_matches=(passshot_df['Team']==team_of_interest)
ax.plot('Passes','Shots', data=passshot_df[team_of_interest_matches], linestyle='none', markersize=6, marker='o', color='red')
ax.set_xticks(np.arange(0,1000,step=100))
ax.set_yticks(np.arange(0,40,step=5))
ax.set_xlabel('Passes (x)')
ax.set_ylabel('Shots (y)')

passshot_df['Shots'] = pd.to_numeric(passshot_df['Shots']) 
passshot_df['Passes'] = pd.to_numeric(passshot_df['Passes']) 
passshot_df['Goals'] = pd.to_numeric(passshot_df['Goals']) 


from sklearn.linear_model import LinearRegression, linear_model

X = np.array(passshot_df['Passes']).reshape(-1,1)
y = np.array(passshot_df['Shots']).reshape(-1,1)

reg = LinearRegression().fit(X, y)

# Line points  
x=np.arange(0,1000,step=0.5).reshape(-1,1)
pred = reg.predict(x)

ax.plot( x, pred, linestyle='-', color='black')
ax.set_ylim(0,40)
ax.set_xlim(0,800) 

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()
fig.savefig('./ShotsPassesWithFit.pdf', dpi=None, bbox_inches="tight") 

#For goals (and strictly speaking even for shots) it is better to do a Poisson regression
poisson_model = linear_model.PoissonRegressor()
b=poisson_model.params



#Make comparative pass maps
x_all=[]
y_all=[]
H_Pass=dict()
for team in teams:
    dp=danger_passes_by[team]
    print(team + str(len(dp)))
    
    x=[]
    y=[]
    for i,apass in dp.iterrows():
        x.append(apass['location'][0])
        y.append(pitchWidthY-apass['location'][1])

    #Make a histogram of passes
    H_Pass[team]=np.histogram2d(y, x,bins=5,range=[[0, pitchWidthY],[0, pitchLengthX]])
    
    x_all = x_all+x
    y_all = y_all+y

H_Pass_All=np.histogram2d(y_all, x_all,bins=5,range=[[0, pitchWidthY],[0, pitchLengthX]])

#Compare to mean
for team in teams:
    (fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')
    pos=ax.imshow(H_Pass[team][0]/number_of_matches[team], aspect='auto',cmap=plt.cm.seismic,vmin=-3, vmax=3)
    pos=ax.imshow(H_Pass[team][0]/number_of_matches[team] - H_Pass_All[0]/(len(matches)*2), extent=[0,120,0,80], aspect='auto',cmap=plt.cm.seismic,vmin=-3, vmax=3)
    #pos=ax.imshow(H_Pass[team][0]/number_of_matches[team] / (H_Pass_All[0]/(len(matches)*2)), extent=[0,120,0,80], aspect='auto',cmap=plt.cm.seismic,vmin=0.5, vmax=2)
    
    ax.set_title('Number of passes per match by ' +team)
    plt.xlim((-1,121))
    plt.ylim((83,-3))
    plt.tight_layout()
    plt.gca().set_aspect('equal', adjustable='box')
    fig.colorbar(pos, ax=ax)
    plt.show()
    
    fig.savefig('Output/PassHeat' + team+ '.pdf', dpi=None, bbox_inches="tight") 