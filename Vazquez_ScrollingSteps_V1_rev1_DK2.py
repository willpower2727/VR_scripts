#This script is a scrolling scene biofeedback exercise. Subjects walk on the treadmill
#at a set speed while "stepping stones" or step length targets appear along the way.
#Subjects are intended to walk on the targets to their best ability. Similar to Guitar Hero
#
#V1 training with biofeedback
#V2P DK2 R1
#
#WDA 2/15/2016

import viz
import vizshape
import time
import vizinfo
import random
import itertools
import socket
import sys
import io
import re
import threading
import Queue
import time
import json
import vizact
import struct
import array
import math
import subprocess
import win32gui
import numpy as np
import oculus
import vizlens

#global cpps
#cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
#time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.go(
#viz.FULLSCREEN #run world in full screen
)
#time.sleep(2)#show off our cool logo, not really required but cool

global targetSL
targetSL = 0.55 #units must be meters

global targettol
targettol = 0.025

global subjectheight
subjectheight = 1.7 #units must be meters

global hmd
#view = viz.addView
# Setup Oculus Rift HMD
hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')
	
# Check if HMD supports position tracking
supportPositionTracking = hmd.getSensor().getSrcMask() & viz.LINK_POS
if supportPositionTracking:
	global man
	# Add camera bounds model
	camera_bounds = hmd.addCameraBounds()
	camera_bounds.visible(True)

	# Change color of bounds to reflect whether position was tracked
	def CheckPositionTracked():
		if hmd.getSensor().getStatus() & oculus.STATUS_POSITION_TRACKED:
			camera_bounds.color(viz.GREEN)
		else:
			camera_bounds.color(viz.RED)
	vizact.onupdate(0, CheckPositionTracked)


# Setup navigation node and link to main view
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())
	
#apply user profile data to view
profile = hmd.getProfile()
if profile:
#	print(profile)
	viewLink.setOffset([0,subjectheight,0])
	hmd.setIPD(profile.ipd)

global beltspeed
beltspeed = 1 #units must be meters/second

global walkdistance
walkdistance = 50/50 #this sets the scale of the walkway length, numerator should be the desired length, denominator is the natural length of the walkway

global walktime
walktime = (walkdistance*50)/beltspeed

global walkway
walkway = viz.addChild('ground.osgb',scale = [0.0167,1,walkdistance])
walkway.setPosition(0,0,(walkdistance*50)/2)#start at one end of the walkway

sky = viz.addChild('sky_day.osgb')
grass1 = viz.addChild('ground_grass.osgb')
grass1.setPosition(0,-0.01,0)
grass2 = viz.addChild('ground_grass.osgb')
grass2.setPosition(0,-0.01,50)
grass3 = viz.addChild('ground_grass.osgb')
grass3.setPosition(0,-0.01,50)


#create a divider line
global divider
divider = vizshape.addQuad(size=(0.01,walkdistance*50),
	axis=-vizshape.AXIS_Y,
	cullFace=False,
	cornerRadius=0)
divider.setPosition(0,0.001,(walkdistance*50)/2)
divider.color(255,255,255)

#make the Right targets
rt = {}
for x in range(1,int((walkdistance*50)/(targetSL*2)),1):
#	rt["T{0}".format(x)]=vizshape.addQuad((0.1,targettol),axis=-vizshape.AXIS_Y,cullFace=False,cornerRadius=0)
	rt["T{0}".format(x)]=vizshape.addBox(size=[0.25,0.02,2*targettol])
	rt["T{0}".format(x)].setPosition(0.2,0.011,x*2*targetSL)
	rt["T{0}".format(x)].color(0,0,0)
	
lt = {}
for x in range(1,int((walkdistance*50)/(targetSL*2)),1):
#	rt["T{0}".format(x)]=vizshape.addQuad((0.1,targettol),axis=-vizshape.AXIS_Y,cullFace=False,cornerRadius=0)
	lt["T{0}".format(x)]=vizshape.addBox(size=[0.25,0.02,2*targettol])
	lt["T{0}".format(x)].setPosition(-0.2,0.011,targetSL+x*2*targetSL)
	lt["T{0}".format(x)].color(0,0,0)
	
#load avatar Mark
#global man
#man = viz.add('mark.cfg')
#rfoot = man.getBone('Bip01 R Foot')
#rfoot.lock()
#rfoot.setEuler(90,0,0)


time.sleep(1)

#generate forward velocity
scroll = vizact.move(0,0,-1*beltspeed,walktime)

#start the movement
walkway.add(scroll)
grass1.add(scroll)
grass2.add(scroll)
grass3.add(scroll)
divider.add(scroll)
for x in range(1,int((walkdistance*50)/(targetSL*2)),1):
	rt["T{0}".format(x)].add(scroll)
	lt["T{0}".format(x)].add(scroll)
	
