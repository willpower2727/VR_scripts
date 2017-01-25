""" Optical Flow Rev4

Visual flow at a set speed, Head tracking enabled, orientation updates only from gyros
No data logging

wda 1/10/2017
"""
import viz
import vizshape
import vizact
import time
import vizinfo
import random
import itertools
import socket
import sys
import io
import re
import csv
import threading
import Queue
import time
import vizact
import struct
import array
import math
import vizlens
import oculus
import subprocess
import vizfx

#global cpps
#cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe"')
#time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
viz.go(
#viz.FULLSCREEN #run world in full screen
)

#in order to move objects
viz.phys.enable()
viz.phys.setGravity(0,0,0) #remove gravity

#setup mono window
monoWindow = viz.addWindow(size=(1,1), pos=(0,1), scene=viz.addScene())
monoQuad = viz.addTexQuad(parent=viz.ORTHO, scene=monoWindow)
monoQuad.setBoxTransform(viz.BOX_ENABLED)
monoQuad.setTexQuadDisplayMode(viz.TEXQUAD_FILL)
texture = vizfx.postprocess.getEffectManager().getColorTexture()

def UpdateTexture():
    monoQuad.texture(texture)
vizact.onupdate(0, UpdateTexture)

global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor()

global navigationNode
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor(),mask=viz.LINK_ORI)

global OF1 #three hallways
global OF2
global OF3

OF1 = viz.addChild('OpticFlowBox6.osgb',scale=[3,3,3])
OF1.disable(viz.LIGHTING)
OF1.collideSphere()

OF2 = viz.addChild('OpticFlowBox6.osgb',scale=[3,3,3])
OF2.disable(viz.LIGHTING)
OF3 = viz.addChild('OpticFlowBox6.osgb',scale=[3,3,3])
OF3.disable(viz.LIGHTING)

#link hallways together so only have to manipulate 1 to get the rest
oblink1 = viz.link(OF1,OF2)
oblink1.postTrans([0,0,1.27*3])
oblink2 = viz.link(OF1,OF3)
oblink2.postTrans([0,0,1.27*6])

navigationNode.setPosition((0,0.15,-1.27*3/2+0.002))
#viz.MainView.setPosition(0,0.15,-1.27*3/2+0.002) 
#viz.MainView.setEuler(0,0,0)

global endflag
endflag = threading.Event()

global scroll
scroll = vizact.move(0,0,-1,5000)

def thread1():
	global endflag
	global navigationNode
	global scroll
	view = viz.MainView
	hmd.getSensor().reset()
	while not endflag.is_set():
#		out = view.getPosition(mode=viz.ABS_GLOBAL)
		out = OF1.getPosition(mode=viz.ABS_GLOBAL)
#		if (out[2] > 1.27*3/2):
		if (out[2] < -1.27*3):
#			view.velocity(0,0,0)
#			view.setPosition(0,0.15,-1.27*3/2+0.002)
#			navigationNode.setPosition((0,0.15,-1.27*3/2+0.002))
			OF1.setPosition(0,0,0)
#			OF1.endAction(pool=0)

#			OF1.setPosition(0,0,1.27*9)

#			print('OF moved')
	print('thread terminated')

def startvel(biggle):
	global navigationNode
	global OF1
	global scroll
	OF1.add(scroll)

#	navigationNode.velocity((0,0,0.4 ))
#	viz.MainView.velocity((0,0,0.4))
	print('moving')

def raisestop(biggle):
	global endflag
	endflag.set()
	viz.quit()
	
def ReCenterView(hmd):
	hmd.getSensor().reset()

t1 = threading.Thread(target=thread1)
t1.start()
vizact.onkeydown('s',startvel,'none')
vizact.onupdate(0, UpdateTexture)
vizact.onkeydown('q',raisestop,'biggle')
vizact.onkeydown('r',ReCenterView,hmd)
