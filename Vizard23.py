#test of forced perspective
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


theta1 = 2*math.atan2(targettolL,2*(1+lensepos))
print("theta1 is: ",theta1)
Rdistance = targettolR*(1+lensepos)/targettolL
print("Rdistance is: ", Rdistance)
theta2 = 2*math.atan2(0.1,2*1.7)#for the width of the right target
rscale1 = Rdistance*math.tan(theta2)

#global boxR #right target box
#boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[1,targettolR,0.0125])
#boxR.setPosition([0.175,0,Rdistance])