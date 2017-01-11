#This script is a scrolling scene biofeedback exercise. Subjects walk on the treadmill
#at a set speed while "stepping stones" or step length targets appear along the way.
#Subjects are intended to walk on the targets to their best ability. Similar to Guitar Hero
#
#V1 training with biofeedback ###################!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*
#V2P DK2 R2 WARNING!!!!!! DK2 R2 NO LONGER STREAMS EULER ANGLES, THIS VERSION WILL CRASH 3/22/2016
#
#Rev 3 uses DK2 markers to track head position and segment data to track orientation
#
#WDA 3/2/2016

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
import vizconnect

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe")
time.sleep(2)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')

#vizconnect.go('vizconnectDK2_displayonly')

viz.go(
#viz.FULLSCREEN #run world in full screen
)
#time.sleep(2)#show off our cool logo, not really required but cool

#try to get handle to display
#view = vizconnect.getDisplay('dk2').getParent()

#print(view)

global targetSL
targetSL = 0.7 #units must be meters

global targettol
targettol = 0.025

global hmd
# Setup Oculus Rift HMD
hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')

# Setup navigation node and link to main view
global navigationNode
navigationNode = viz.addGroup()
global viewLink
viewLink = viz.link(navigationNode, viz.MainView)

#apply user profile data to view
profile = hmd.getProfile()
if profile:
	print(profile)
#	viewLink.setOffset([0,subjectheight,0])
	hmd.setIPD(profile.ipd)


def ReCenterView(hmd):
	hmd.getSensor().reset()

global beltspeed
beltspeed = 1 #units must be meters/second

global walkdistance
walkdistance = 50/50 #this sets the scale of the walkway length, numerator should be the desired length, denominator is the natural length of the walkway

global walktime
walktime = (walkdistance*50)/beltspeed

global walkway
walkway = viz.addChild('ground.osgb',scale = [0.0167,1,walkdistance])
walkway.setPosition(0.462,0,(walkdistance*50)/2)#start at one end of the walkway

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
divider.setPosition(0.462,0.001,(walkdistance*50)/2)
divider.color(255,255,255)

#make the Right targets
rt = {}
tlocs = {}
for x in range(1,int((walkdistance*50)/(targetSL*2)),1):
#	rt["T{0}".format(x)]=vizshape.addQuad((0.1,targettol),axis=-vizshape.AXIS_Y,cullFace=False,cornerRadius=0)
	rt["T{0}".format(x)]=vizshape.addBox(size=[0.25,0.02,2*targettol])
	rt["T{0}".format(x)].setPosition(0.462+0.2,0.011,x*2*targetSL)
	tlocs["T{0}".format(x)]=x*2*targetSL
	rt["T{0}".format(x)].color(0,0,0)
#print(tlocs)
lt = {}
for x in range(1,int((walkdistance*50)/(targetSL*2)),1):
#	rt["T{0}".format(x)]=vizshape.addQuad((0.1,targettol),axis=-vizshape.AXIS_Y,cullFace=False,cornerRadius=0)
	lt["T{0}".format(x)]=vizshape.addBox(size=[0.25,0.02,2*targettol])
	lt["T{0}".format(x)].setPosition(0.462-0.2,0.011,targetSL+x*2*targetSL)
	lt["T{0}".format(x)].color(0,0,0)
	
#load avatar Mark
#global man
#man = viz.add('mark.cfg')
#man = viz.add('vcc_male.cfg')
#man.disable(viz.LIGHTING)
#man.setPosition(0,0,-0.5)
#global rfoot
#rfoot = man.getBone('Bip01 R Foot')
#rfoot.lock()
#global rcalf
#rcalf = man.getBone('Bip01 R Calf')
#rcalf.lock()
#global rthigh
#rthigh = man.getBone('Bip01 R Thigh')
#rthigh.lock()
#global lfoot
#lfoot = man.getBone('Bip01 L Foot')
#lfoot.lock()
#global lcalf
#lcalf = man.getBone('Bip01 L Calf')
#lcalf.lock()
#global lthigh
#lthigh = man.getBone('Bip01 L Thigh')
#lthigh.lock()

#create foot squares
global rmark
rmark = vizshape.addBox(size=(.025,.025,.025))
rmark.color(255,0,0)
rmark.setPosition(0,0,0)

global lmark
lmark = vizshape.addBox(size=(.025,.025,.025))
lmark.color(0,255,0)
lmark.setPosition(0,0,0)

global alphastack
alphastack = [0] * 5
global betastack
betastack = [0] * 5
global gammastack
gammastack = [0] * 5

global firsttime
firsttime = 1


#setup rotation matrix
a0 = -8.57*math.pi/180
b0 = 86.417*math.pi/180
g0 = -11.31*math.pi/180

Ra0 = np.matrix([[1,0,0],[0, float(math.cos(a0)), float(-1*math.sin(a0))],[0,float(math.sin(a0)),float(math.cos(a0))]],dtype=np.float)
Rb0 = np.matrix([[math.cos(b0),0,math.sin(b0)],[0,1,0],[-1*math.sin(b0),0,math.cos(b0)]],dtype=np.float)
Rg0 = np.matrix([[math.cos(g0),-1*math.sin(g0),0],[math.sin(g0),math.cos(g0),0],[0,0,1]],dtype=np.float)

global RhmdU0 
RhmdU0 = Ra0*Rb0*Rg0

global RdU0
#RdU0 = np.matrix([[-1,0,0],[0,1,0],[0,0,1]],dtype=np.float)
RdU0 = np.matrix([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float)

#print(RdU0)


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
	

def InverseK(at,bt,gt):
	global RdU0
	global RhmdU0

	S = np.matrix([[1,0,0],[0,1,0],[0,0,-1]],dtype=np.float)
	Rvv = np.matrix([[-1,0,0],[0,0,1],[0,1,0]],dtype=np.float)
	
	#given 3 Euler sequence in right-handed vicon space,
	Rat = np.matrix([[1,0,0],[0, math.cos(at), -1*math.sin(at)],[0,math.sin(at),math.cos(at)]],dtype=np.float)
	Rbt = np.matrix([[math.cos(bt),0,math.sin(bt)],[0,1,0],[-1*math.sin(bt),0,math.cos(bt)]],dtype=np.float)
	Rgt = np.matrix([[math.cos(gt),-1*math.sin(gt),0],[math.sin(gt),math.cos(gt),0],[0,0,1]],dtype=np.float)
	
	RhmdUt = Rat*Rbt*Rgt
	
	RdUt = RhmdUt*RhmdU0.transpose()*RdU0
	
	RdUt = S*RdUt*S #make it left handed
	
	#do a matrix conditioning check, seems some degrees of freedom are colluded
#	determ = np.linalg.det(RdUt)
#	print('Rotation Matrix Determinant: ',determ)
#	print('R*Rt: ',RdUt*RdUt.transpose())
	
	
#	RdUt = RdUt*np.matrix([[-1,0,0],[0,0,-1],[0,1,0]])
	
	#do inverse K to get euler sequence out:
#	beta = math.atan2(-RdUt[0,1],math.sqrt(RdUt[1,1]**2+RdUt[2,1]**2))
#	alpha = math.atan2(RdUt[1,1]/math.cos(beta),RdUt[2,1]/math.cos(beta))
#	gamma = math.atan2(-RdUt[0,2]/math.cos(beta),-RdUt[0,0]/math.cos(beta))

#	alpha = math.atan2(-1*RdUt[1,2],RdUt[2,2])
#	beta = math.atan2(RdUt[0,2],RdUt[2,2]/math.cos(alpha))
#	gamma = math.atan2(-1*RdUt[0,1]/math.cos(beta),RdUt[0,0]/math.cos(beta))

#	alpha = math.atan2(RdUt[1,2],math.sqrt(RdUt[0,2]**2+RdUt[2,2]**2))
#	beta = math.atan2(-RdUt[0,2]/math.cos(alpha),RdUt[2,2]/math.cos(alpha))
#	gamma = math.atan2(-RdUt[1,0]/math.cos(alpha),RdUt[1,1]/math.cos(alpha))

	beta = math.atan2(-1*RdUt[0,2],RdUt[2,2])
	alpha = math.atan2(RdUt[1,2],RdUt[2,2]/math.cos(beta))
	gamma = math.atan2(-1*RdUt[1,0]/math.cos(alpha),RdUt[1,1]/math.cos(alpha))
	
	
	return(alpha,beta,gamma)
	
#tester = InverseK(-177.9*math.pi/180,31.2*math.pi/180,90.4*math.pi/180)
#print('test= ',tester)
	
def UpdateViz(root,q):#,speedlist,qq,savestring,q3):

#	global hmd
#	hmd.getSensor().reset()
	
	while not endflag.isSet():
		
#		global man
#		global rfoot
#		global rcalfq
#		global rthigh
#		global lfoot
#		global lcalf
#		global lthigh
		global rmark
		global lmark
		global viewLink
		global alphastack
		global betastack
		global gammastack
		global navigationNode
		global firsttime
		
		
		root = q.get()
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
#		try:
		RANKX = float(data["RANK"][0])/1000
		LANKX = float(data["LANK"][0])/1000
		RANKY = float(data["RANK"][1])/1000
		LANKY = float(data["LANK"][1])/1000
		RANKZ = float(data["RANK"][2])/1000
		LANKZ = float(data["LANK"][2])/1000
		
		#rotations of HMD segment
		HMDRX = float(data["HMDr"][0])#*180/math.pi #make sure to convert to degrees
		HMDRY = float(data["HMDr"][1])#*180/math.pi
		HMDRZ = float(data["HMDr"][2])#*180/math.pi
		#HMD markers
		HMDX = float(data["HMDp"][0])/1000
		HMDY = float(data["HMDp"][1])/1000
		HMDZ = float(data["HMDp"][2])/1000
#		except:
#			print('not all marker data available...')
		'''
#		rcalf.setEuler(0,0,-1*180/math.pi*float(data["RightTibia"][1]))
#		rthigh.setEuler(180,0,-1*180/math.pi*float(data["RightFemur"][1])-20)
#		rfoot.setEuler(0,0,-1*180/math.pi*float(data["RightFoot"][1]))
#		lcalf.setEuler(0,0,-1*180/math.pi*float(data["LeftTibia"][1]))
#		lthigh.setEuler(180,0,-1*180/math.pi*float(data["LeftFemur"][1])-20)
#		lfoot.setEuler(0,0,-1*180/math.pi*float(data["LeftFoot"][1]))
		'''

#		print('HMDRX: ',HMDRX*180/math.pi,' HMDRY: ',HMDRY*180/math.pi,' HMDRZ : ',HMDRZ*180/math.pi)
		
		alphastack.append(np.mean(np.array([HMDX],dtype=float)))
		alphastack.pop(0)
		betastack.append(np.mean(np.array([HMDY],dtype=float)))
		betastack.pop(0)
		gammastack.append(np.mean(np.array([HMDZ],dtype=float)))
		gammastack.pop(0)
		

		#one time only pre-euler offset
#		if (firsttime == 1):
#			viewLink.preEuler([90,180,30])
#			firsttime = 0
			
		angles = InverseK(HMDRX,HMDRY,HMDRZ)
#		print(angles[0]*180/math.pi,angles[1]*180/math.pi,angles[2]*180/math.pi)
#		viewLink.preEuler([-90,180,30])
#		viewLink.postEuler([HMDRZ,HMDRX,-1*(HMDRY)])
#		viewLink.setEuler([HMDRZ,HMDRX,-1*(HMDRY)])#correct?

#		navigationNode.setEuler(-1*angles[2]*180/math.pi,angles[0]*180/math.pi,angles[1]*180/math.pi)
#		
		navigationNode.setEuler(angles[2]*180/math.pi,angles[0]*180/math.pi,angles[1]*180/math.pi)
		


		
#		navigationNode.setEuler(HMDRZ-90,HMDRX+180,-1*(HMDRY)+30)

		navigationNode.setPosition([-1*np.mean(alphastack),np.mean(gammastack),-1*np.mean(betastack)])

		rmark.setPosition(-1*RANKX,RANKZ-0.05,-1*RANKY)
		lmark.setPosition(-1*LANKX,LANKZ-0.05,-1*LANKY)
		
	cpps.kill()
		

def runclient(root,q):
	
	#illegal characters to remove from string later before going to xml
	RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
					 u'|' + \
					 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
					  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
					   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
					   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
	HOST = 'localhost'#IP address of CPP server
	PORT = 50008
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print 'Socket created'
	print 'Socket now connecting'
	s.connect((HOST,PORT))
	s.send('1')#send initial request for data
	while not endflag.isSet():
		global FNold
		global repeatcount
		data = s.recv(50)#receive the initial message
		data3 = data[:3]#get first 3 letters
		if (data3 == "New"):
			nextsizestring = data[3:]#get the integer after "New"
			nextsizestring2 = nextsizestring.rstrip('\0')#format
			nextsize = int(nextsizestring2,10)#cast as type int
#			print("Next Packet is size: ")
#			print(nextsize)
			s.send('b')#tell cpp server we are ready for the packet
			databuf = ''#initialize a buffer
			while (sys.getsizeof(databuf) < nextsize):
				data = s.recv(nextsize)#data buffer as a python string
				databuf = databuf + data#collect data into buffer until size is matched
			root = databuf
#			print('root',root)
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			q.put(root)#place the etree into the threading queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()
	
	
def ParseRoot(root):#the purpose of this function is to make sure that marker data is used correctly since they can arrive in different order, depending on the order the models are listed in Nexus
	tempdat = root.split(',')
#	print tempdat
	del tempdat[-1]#the last element is a empty string ""
	data = {}#create dictionary
	
	data["FN"] = int(tempdat[0])#frame number
	data["Rz"] = float(tempdat[4])#right forceplate Z component
	data["Lz"] = float(tempdat[2])#left forceplate Z comp.
	data["DeviceCount"] = float(tempdat[5])# #of devices besides forceplates
	for x in range(6,6+2*int(data["DeviceCount"])-1,2):  #assumes one value per device for now...
		temp = tempdat[x]
		data[temp] = [tempdat[x+1]]
#		print temp
	
	#place marker data into dictionary
	for z in range(6+2*int(data["DeviceCount"]),len(tempdat),4):
		temp = tempdat[z]
#		print temp
		data[temp] = [tempdat[z+1],tempdat[z+2],tempdat[z+3]]
		
#	print(data)
	return data
	
endflag = threading.Event()#an event to raise when we are ready to stop recording
def raisestop(sign):
	#the sign passed in doesn't do anything, I just didn't know how to make this work without passing something in...
	print("stop flag raised")
	endflag.set()
	t1.join(5)
	t2.join(5)
#	t4.join(5)
	viz.quit()
	
root = ''#empty string
#savestring = ''
#speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q))#,speedlist,qq,savestring,q3))
#t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
#t4.daemon = True
#start the threads
t1.start()
t2.start()
#t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
#vizact.onkeydown('r',ReCenterView,hmd)#biggle is meaningless, just need to pass something into the raisestop callback
	