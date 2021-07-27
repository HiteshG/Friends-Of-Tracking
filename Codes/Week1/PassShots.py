# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 07:26:37 2021

@author: Hitesh
"""

#Exercise: 
#1, Create a dataframe of passes which contains all the passes in the match
#2, Plot the start point of every Sweden pass. Attacking left to right.
#3, Plot only passes made by Caroline Seger (she is Sara Caroline Seger in the database)
#4, Plot arrows to show where the passes


import json
import pandas as pd
import matplotlib.pyplot as plt
loc = "C:/Users/Harry/Data Science Sports/data/"

#ID for England vs Sweden Womens World Cup
match_id_required = 69301
team_required = "Sweden Women's"

file_name = str(match_id_required)+'.json'

#Load in match events for ID 69301

with open(loc + "StatsBomb/data/" + "events/" + file_name ) as f:
    events = json.load(f)
    
# store the dataframe in a dictionary with the match id as key (remove '.json' from string)
# Assign function creates a new column with value in DataFrame
df = pd.json_normalize(events, sep = "_").assign(match_id = file_name[:-5])

#Answer 1.Pass Selection Only
passes = df[df["type_name"] == "Pass"].set_index("id")

#Size of the pitch in yards (StatsBomb)
pitchLengthX = 120
pitchWidthY = 80

#Draw the pitch using FCPython package 
from FCPython import createPitch
(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')

#Answer 2. Plot the passing start point
for i, Pass in passes.iterrows():
    
    if(Pass['team_name'] == team_required):
        
        # Starting Points
        x=Pass['location'][0]
        y=Pass['location'][1]

        circleSize= 1.5
        
        passCircle = plt.Circle( (x, pitchWidthY - y),circleSize, color = "red")
        passCircle.set_alpha(.2)
        ax.add_patch(passCircle)
    
total_pass = passes[passes['team_name']== team_required ]["index"].count()

plt.text(45,82, team_required + ' Total Passes -'+ str(total_pass) )
     
fig.set_size_inches(10, 7)
fig.savefig('Output/{} Pass.jpeg'.format(team_required), dpi=100) 
plt.show()

#Answer3. Plot the passing start point for Player "Sara Caroline Seger"

(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')

player_name = "Sara Caroline Seger"
player_pass = passes[(passes['team_name'] == team_required) &
                     (passes['player_name'] == player_name)]

# Plot the passing start point
for i, Pass in player_pass.iterrows():
       
        # Starting Points
        x=Pass['location'][0]
        y=Pass['location'][1]

        circleSize= 1.5
        
        passCircle = plt.Circle( (x, pitchWidthY - y),circleSize, color = "blue")
        passCircle.set_alpha(.2)
        ax.add_patch(passCircle)
    
total_pass = player_pass["index"].count()

plt.text(45,82, player_name + ' Total Passes-' + str(total_pass) )
     
fig.set_size_inches(10, 7)
fig.savefig('Output/{} Pass.jpeg'.format(player_name), dpi=100) 
plt.show()

#Answer4. Plot the pass arrows for Player "Sara Caroline Seger"

(fig,ax) = createPitch(pitchLengthX,pitchWidthY,'yards','gray')

# Plot the passing start point
for i, Pass in player_pass.iterrows():
       
        # Starting Points
        x=Pass['location'][0]
        y=Pass['location'][1]

        circleSize= 1.5
        
        passCircle = plt.Circle( (x, pitchWidthY - y),circleSize, color = "blue")
        passCircle.set_alpha(.2)
        ax.add_patch(passCircle)
        
        dx = Pass['pass_end_location'][0] - x
        dy = Pass['pass_end_location'][1] - y
        
        passArrow=plt.Arrow(x,pitchWidthY-y, dx, -dy, width=2,color="blue")
        ax.add_patch(passArrow)
      
    
total_pass = player_pass["index"].count()

plt.text(45,82, player_name + ' Total Passes-' + str(total_pass) )
     
fig.set_size_inches(10, 7)
fig.savefig('Output/{} PassingArrow.jpeg'.format(player_name), dpi=100) 
plt.show()
