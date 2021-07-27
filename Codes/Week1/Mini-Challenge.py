# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 18:57:53 2021

@author: Hitesh
"""

#Exercise: 
#1, Think of player from Women's World Cup or Men's World Cup
#2, What action they perform and importance and why
#3, Plot your insights


import json
import pandas as pd
import matplotlib.pyplot as plt
loc = "C:/Users/Harry/Data Science Sports/data/"

#ID for France vs Croatia Men's World Cup
match_id_required = 8658
team_required = "France"

file_name = str(match_id_required)+'.json'

#Load in match events for ID 69301

with open(loc + "StatsBomb/data/" + "events/" + file_name ) as f:
    events = json.load(f)
    
# store the dataframe in a dictionary with the match id as key (remove '.json' from string)
# Assign function creates a new column with value in DataFrame
df = pd.json_normalize(events, sep = "_").assign(match_id = file_name[:-5])

#Size of the pitch in yards (StatsBomb)
pitchLengthX = 120
pitchWidthY = 80

df = df[(df["team_name"] == team_required)].set_index("id")
passes = df[(df["type_name"] == "Pass")]

#Draw the pitch using FCPython package 
from FCPython import createPitch
(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')

#Answer 2. Plot the passing start point
for i, Pass in passes.iterrows():
    
        # Starting Points
        x=Pass['location'][0]
        y=Pass['location'][1]

        circleSize= 1.5
        
        passCircle = plt.Circle( (x, pitchWidthY - y),circleSize, color = "blue")
        passCircle.set_alpha(.2)
        ax.add_patch(passCircle)
    
total_pass = passes["index"].count()

plt.text(45,82, team_required + ' Total Passes -'+ str(total_pass) )
plt.text(30, -5, "Observation: Most of the passes where from left wing")
fig.set_size_inches(10, 7)
fig.savefig('Output/{} WorldCupFinalsPass.jpeg'.format(team_required), dpi=100) 
plt.show()


# N\"Golo Kanté was much appreciated player of the match. Let's dig more 

# Total Pass Control by Kante of 292
player_id = 3961






