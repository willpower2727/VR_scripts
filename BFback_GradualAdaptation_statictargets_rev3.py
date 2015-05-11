#script runs biofeedback routine with TMM, Vicon. Gives feedback on the length of step 

#revision 3 makes it possible to have different targets for the L and R legs, but they appear the same
#WDA
#2/12/2015

import socket
import sys
import io
import re
from xml.etree import ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
import math

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go()

lensepos = 0.7
viz.MainView.setPosition(0,0,-lensepos)
viz.MainView.setEuler(0,0,0)


#set target tolerance for stride length
global targetL
targetL = 0.565
global targetR
targetR = 0.565

global targettolR
global targettolL
targettolL = 0.05
targettolR = 0.07

#compute the perspective variables
#assume the left target stays put

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettolL,0.0125])
boxL.setPosition([-0.175,0,1])

cscale = boxL.getScale(	 mode = viz.ABS_PARENT	) 

print 'cscale is:'
print str(cscale)
global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[1.2*cscale[0],targetL,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.175,-targetL,1])
cursorL.visible(0)
global neutralL
neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[1.2*cscale[0],0.5*cscale[1],0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.175,-targetL,1])
global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.8*targettolL,0.8*targettolL,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.175,0,1])
HistBallL.alpha(0.8)

global lscaler
lscaler = 1

###############
theta1 = targettolL/(1+lensepos)
print("theta1 is: ",theta1)
Rdistance = targettolL*(1+lensepos)/targettolR
print("Rdistance is: ", Rdistance)
theta2 = 2*math.atan2(0.1,2*1.7)#for the width of the right target
rscale1 = Rdistance*math.tan(theta2)


theta3 = 2*math.atan2(0.175,2*1)#for the Left to Right position of the Right target
rxdistance = Rdistance*math.tan(theta3)
theta4 = 2*math.atan2(targetL,2*1)#for the initial height of the cursor
rcursescale = Rdistance*math.tan(theta4)

global rscaler
rscaler = 0.25/targetR

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[1,targettolR,0.0125])
boxR.setPosition([0.175,0,Rdistance])








