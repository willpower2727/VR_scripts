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

global targetR
global targetL
targetR = 0.25
targetL = 0.25
global targettol
targettol = 0.025

ttL = 0.05

#targetR = viz.addTexQuad(pos=[0.1,0,0],scale = [.2,2*targettol,0])
#targetR.color(0,0.5,1)

viz.startLayer(viz.LINES) 
viz.vertex(0,1,-0.0001) #Vertices are split into pairs. 
viz.vertex(0,-1,-0.0001) 
myLines = viz.endLayer() 

viz.startLayer(viz.LINES) 
viz.vertex(-1,0,-0.0001) #Vertices are split into pairs. 
viz.vertex(1,0,-0.0001) 
myLines = viz.endLayer()

viz.startLayer(viz.LINES) 
viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
viz.vertex(1,-0.25,-0.0001) 
myLines = viz.endLayer() 

targetR = viz.addTexQuad(pos=[0.2,0,0],scale = [.2,2*targettol,0])
targetR.color(0,0.5,1)

viz.MainView.setPosition(0, 0, -1)
viz.MainView.setEuler(0,0,0)

#math for view angles
theta1 = 2*math.atan2(targettol,2*1)
print(theta1)
distanceL = ttL/(2*math.tan(theta1/2))
print(distanceL)

theta2 = 2*math.atan2(0.2,2*1)
print(theta2)
widthL = 2*(distanceL)*math.tan(theta2/2)
print(widthL)


targetL = viz.addTexQuad(pos=[-widthL,0,distanceL-1],scale = [widthL,2*ttL,0])
targetL.color(0,0.5,1)
targetL.color(viz.WHITE)
#targetL.disable(viz.LIGHTING)
#targetL.alpha(1.1)

box = viz.add('box3.obj',scale=[0.1,0.25,0.001],color=[1,1,1])
box.setPosition(0,-0.25,0)
box.disable(viz.LIGHTING)

