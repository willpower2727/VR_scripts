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

#viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
#viz.FULLSCREEN
)

targettol = 0.025
boxL = viz.addChild('target2.obj',color=viz.WHITE,scale=[0.1,0.005,targettol*2])
boxL.setPosition([0,0,0])
boxL.setEuler(0,90,0)

origin  = viz.addChild('box.wrl',color=viz.GREEN,scale=[0.1,0.0009,0.001])
origin.setPosition([0,0,0])

h = viz.addChild('box.wrl',color=viz.RED,scale=[0.1, 0.0009, 0.001])
h.setPosition([0,-targettol,0])

g = viz.addChild('box.wrl',color=viz.RED,scale=[0.1,0.0009,0.001])
g.setPosition([0,+targettol,0])

viz.MainView.setPosition(0, 0, -0.3)
viz.MainView.setEuler(0,0,0)
#
#while 1:
#	continue
