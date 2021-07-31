"""
Fitting the xG model
Need to run 3xGModel.py first to load data.
"""
#The basics
import pandas as pd
import numpy as np

#Plotting
import matplotlib.pyplot as plt
import FCPython 


shots_model = pd.read_csv("./shots.csv")
goals_only = pd.read_csv("./goals.csv")
#Get first 200 shots
shots_200=shots_model.iloc[:200]

#Plot first 200 shots goal angle
fig,ax=plt.subplots(num=1)
ax.plot(shots_200['Angle']*180/np.pi, shots_200['Goal'], linestyle='none', marker= '.', markerSize= 12, color='black')
ax.set_ylabel('Goal scored')
ax.set_xlabel("Shot angle (degrees)")
plt.ylim((-0.05,1.05))
ax.set_yticks([0,1])
ax.set_yticklabels(['No','Yes'])
plt.show()

#Show empirically how goal angle predicts probability of scoring
shotcount_dist=np.histogram(shots_model['Angle']*180/np.pi,bins=40,range=[0, 150])
goalcount_dist=np.histogram(goals_only['Angle']*180/np.pi,bins=40,range=[0, 150])
prob_goal=np.divide(goalcount_dist[0],shotcount_dist[0])
angle=shotcount_dist[1]
# midangle is mid point angle form will putting shots in bucket size of 40
midangle= (angle[:-1] + angle[1:])/2
fig,ax=plt.subplots(num=2)
ax.plot(midangle, prob_goal, linestyle='none', marker= '.', markerSize= 12, color='black')
ax.set_ylabel('Probability chance scored')
ax.set_xlabel("Shot angle (degrees)")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Understanding purpose
# This is a good model but NOT a good way of fitting.
# because each point contains lots of data points
b=[3, -3]
x=np.arange(150,step=0.1)
y=1/(1+np.exp(b[0]+b[1]*x*np.pi/180)) 
ax.plot(x, y, linestyle='solid', color='black')
plt.show()

#Now lets look at the likelihood of model given data
xG=1/(1+np.exp(b[0]+b[1]*shots_model['Angle'])) 
shots_model = shots_model.assign(xG=xG)
shots_40=shots_model.iloc[:40]
fig,ax=plt.subplots(num=1)
ax.plot(shots_40['Angle']*180/np.pi, shots_40['Goal'], linestyle='none', marker= '.', markerSize= 12, color='black')
ax.plot(x, y, linestyle='solid', color='black')
ax.plot(x, 1-y, linestyle='solid', color='black')
loglikelihood=0
for item,shot in shots_40.iterrows():
    ang=shot['Angle']*180/np.pi
    if shot['Goal']==1:
        loglikelihood=loglikelihood+np.log(shot['xG'])
        ax.plot([ang,ang],[shot['Goal'],shot['xG']], color='red')
    else:
        loglikelihood=loglikelihood+np.log(1 - shot['xG'])
        ax.plot([ang,ang],[shot['Goal'],1-shot['xG']], color='blue')
    
ax.set_ylabel('Goal scored')
ax.set_xlabel("Shot angle (degrees)")
plt.ylim((-0.05,1.05))
plt.xlim((0,80))
plt.text(45,0.2,'Log-likelihood:') 
plt.text(45,0.1,str(loglikelihood))
ax.set_yticks([0,1])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()


#Make single variable model of angle
#Using logistic regression we find the optimal values of b
#This process minimizes the loglikelihood
X = np.array(shots_model["Angle"]).reshape(-1,1)
y = shots_model["Goal"] 

from sklearn.linear_model import LogisticRegression
test_model = LogisticRegression(random_state=0).fit(X, y)
print(test_model.get_params())
b0 = test_model.intercept_
b1 = test_model.coef_

xGprob=1/(1+np.exp(b1+b0*midangle*np.pi/180)) 
xGprob = (xGprob.reshape(-1,1))
fig,ax=plt.subplots(num=1)
ax.plot(midangle, prob_goal, linestyle='none', marker= '.', markerSize= 12, color='black')
ax.plot(midangle, xGprob, linestyle='solid', color='black')
ax.set_ylabel('Probability chance scored')
ax.set_xlabel("Shot angle (degrees)")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()
fig.savefig('./ProbabilityOfScoringAngleFit.pdf', dpi=None, bbox_inches="tight")   


#Now lets look at distance from goal

shots_model = pd.read_csv("./shots.csv")
goals_only = pd.read_csv("./goals.csv")

#Show empirically how distance from goal predicts probability of scoring
shotcount_dist=np.histogram(shots_model['Distance'],bins=40,range=[0, 70])
goalcount_dist=np.histogram(goals_only['Distance'],bins=40,range=[0, 70])
prob_goal=np.divide(goalcount_dist[0],shotcount_dist[0])
distance=shotcount_dist[1]
middistance= (distance[:-1] + distance[1:])/2
fig,ax=plt.subplots(num=1)
ax.plot(middistance, prob_goal, linestyle='none', marker= '.', color='black')
ax.set_ylabel('Probability chance scored')
ax.set_xlabel("Distance from goal (metres)")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

#Make single variable model of distance
X = np.array(shots_model["Distance"]).reshape(-1,1)
y = shots_model["Goal"] 

test_model = LogisticRegression(random_state=0).fit(X, y)
print(test_model.get_params())
b0 = test_model.intercept_
b1 = test_model.coef_

xGprob=1/(1+np.exp(b1+b0*middistance)) 
xGprob = (xGprob.reshape(-1,1))
ax.plot(middistance, xGprob, linestyle='solid', color='black')
plt.show()
fig.savefig('./ProbabilityOfScoringDistance.pdf', dpi=None, bbox_inches="tight")  


model_variables = ["Angle", "Distance"]
X = shots_model[model_variables]
y = shots_model["Goal"]
clf = LogisticRegression(random_state=0).fit(X, y)

#Return xG value for more general model
def calculate_xG(sh):
    val = np.array(list(sh.values())).astype(float)
    val = val.reshape(1,-1)
    xGvalue = clf.predict(val)
    return xGvalue

#Create a 2D map of xG
pgoal_2d=np.zeros((65,65))
for x in range(65):
    for y in range(65):
        sh=dict()
        a = np.arctan(7.32 *x /(x**2 + abs(y-65/2)**2 - (7.32/2)**2))
        if a<0:
            a = np.pi + a
        sh['Angle'] = a
        sh['Distance'] = np.sqrt(x**2 + abs(y-65/2)**2)
        
        pgoal_2d[x,y] =  calculate_xG(sh)

(fig,ax) = FCPython.createGoalMouth()
pos=ax.imshow(pgoal_2d, extent=[-1,65,65,-1], aspect='auto',cmap=plt.cm.Reds,vmin=0, vmax=0.3)
fig.colorbar(pos, ax=ax)
ax.set_title('Probability of goal')
plt.xlim((0,66))
plt.ylim((-3,35))
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
fig.savefig('./goalprobfor_' + "LogReg"  + '.pdf', dpi=None, bbox_inches="tight")   