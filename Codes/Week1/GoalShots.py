# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 07:26:37 2021

@author: Hitesh
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

loc = "C:/Users/Harry/Data Science Sports/data/"

#ID for England vs Sweden Womens World Cup
match_id_required = 69301
home_team_required = "England Women's"
away_team_required = "Sweden Women's"

file_name = str(match_id_required)+'.json'

#Load in match events for ID 69301

with open(loc + "StatsBomb/data/" + "events/" + file_name ) as f:
    events = json.load(f)
    
# store the dataframe in a dictionary with the match id as key (remove '.json' from string)
# Assign function creates a new column with value in DataFrame
df = pd.json_normalize(events, sep = "_").assign(match_id = file_name[:-5])

# Shots Selection Only
shots = df[df["type_name"] == "Shot"].set_index("id")

#Size of the pitch in yards (StatsBomb)
pitchLengthX = 120
pitchWidthY = 80

#Draw the pitch using FCPython package 
from FCPython import createPitch
(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')


#Plot the shots
for i,shot in shots.iterrows():
    x=shot['location'][0]
    y=shot['location'][1]
    
    # Looking Goals only
    goal=shot['shot_outcome_name']=='Goal'
    team_name=shot['team_name']
    
    circleSize=2
    
    # StatsBomb have Expected Goals model.
    # *11 is a random number based on how well visualization was looking
    # Probability lies btw 0 & 1. So, sqrt of number less than 1 > number itself
    circleSize= np.sqrt(shot['shot_statsbomb_xg'])*11
    
    if (team_name==home_team_required):
        # print("Home - x:{} , y:{} ".format(x, y))
        if goal:
            shotCircle=plt.Circle((x,pitchWidthY-y),circleSize,color="red")
            plt.text((x+1),pitchWidthY-y+1,shot['player_name']) 
        else:
            shotCircle=plt.Circle((x,pitchWidthY-y),circleSize,color="red")     
            shotCircle.set_alpha(.2)
    elif (team_name==away_team_required):
        # print("Away - x: {}, y: {}".format(x, y))
        if goal:
            shotCircle=plt.Circle((pitchLengthX-x,y),circleSize,color="blue") 
            plt.text((pitchLengthX-x+1),y+1,shot['player_name']) 
        else:
            shotCircle=plt.Circle((pitchLengthX-x,y),circleSize,color="blue")      
            shotCircle.set_alpha(.2)
    ax.add_patch(shotCircle)
    
total_home_shots = shots[shots['team_name']== home_team_required ]["index"].count()
total_away_shots = shots[shots['team_name']== away_team_required ]["index"].count()

plt.text(5,75,away_team_required + ' shots -' + str(total_away_shots) )
plt.text(80,75,home_team_required + ' shots -'+ str(total_home_shots) )
     
fig.set_size_inches(10, 7)
fig.savefig('Output/shots.pdf', dpi=100) 
plt.show()


#Exercise: 
#1, Create a dataframe of passes which contains all the passes in the match
#2, Plot the start point of every Sweden pass. Attacking left to right.
#3, Plot only passes made by Caroline Seger (she is Sara Caroline Seger in the database)
#4, Plot arrows to show where the passes where
