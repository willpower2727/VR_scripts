#This script is a scrolling scene biofeedback exercise. Subjects walk on the treadmill
#at a set speed while "stepping stones" or step length targets appear along the way.
#Subjects are intended to walk on the targets to their best ability. Similar to Guitar Hero
#
#V1 training with biofeedback
#V2P DK2 R2
#
#Rev 6 introduces kalman filter on orientation
#
#WDA 3/25/2016

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
import pykalman

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe")
time.sleep(2)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')


viz.go(
#viz.FULLSCREEN #run world in full screen
)

global targetSL
targetSL = 0.7 #units must be meters

global targettol
targettol = 0.025

global hmd
# Setup Oculus Rift HMD
hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')
else:
	profile = hmd.getProfile()
	hmd.setIPD(profile.ipd)
	
# Setup navigation node and link to main view
global navigationNode
navigationNode = viz.addGroup()
global viewLink
viewLink = viz.link(navigationNode, viz.MainView)

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
	

#create foot squares
global rmark
rmark = vizshape.addBox(size=(.025,.025,.025))
rmark.color(255,0,0)
rmark.setPosition(0,0,0)

global lmark
lmark = vizshape.addBox(size=(.025,.025,.025))
lmark.color(0,255,0)
lmark.setPosition(0,0,0)

#for smoothing position/orientation tracking
global alphastack
alphastack = [0] * 5
global betastack
betastack = [0] * 5
global gammastack
gammastack = [0] * 5
global xstack
xstack = [0] * 5
global ystack
ystack = [0] * 5
global zstack
zstack = [0] * 5


#setup rotation matrix for constant transform between headset and looking forward
a0 = -8.57*math.pi/180
b0 = 86.417*math.pi/180
g0 = -11.31*math.pi/180

Ra0 = np.matrix([[1,0,0],[0, float(math.cos(a0)), float(-1*math.sin(a0))],[0,float(math.sin(a0)),float(math.cos(a0))]],dtype=np.float)
Rb0 = np.matrix([[math.cos(b0),0,math.sin(b0)],[0,1,0],[-1*math.sin(b0),0,math.cos(b0)]],dtype=np.float)
Rg0 = np.matrix([[math.cos(g0),-1*math.sin(g0),0],[math.sin(g0),math.cos(g0),0],[0,0,1]],dtype=np.float)

global RhmdU0 
RhmdU0 = Rg0*Rb0*Ra0 

global RdU0
RdU0 = np.matrix([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float)

global viconmat
viconmat = np.matrix([[0,0,0],[0,0,0],[0,0,0]],dtype=np.float)

global X #k-1 timestep state estimate initiated as zeros
X = np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float)

global P #state coavariance prediction
P = np.diag((0.01,0.01,0.01,0.01,0.01,0.01))
#print(P)
dt = 0
global A #system matrix
A = np.array([[1,0,0,dt,0,0],[0,1,0,0,dt,0],[0,0,1,0,0,dt],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]],dtype=np.float)

xshape = X.shape
dq = 0.35
global Q #process noise covariance
#Q = np.eye(xshape[0])
Q = np.array([[dq,0,0,0,0,0],[0,dq,0,0,0,0],[0,0,dq,0,0,0],[0,0,0,dq,0,0],[0,0,0,0,dq,0],[0,0,0,0,0,dq]],dtype=np.float)

global B #system input matrix
B = np.eye(xshape[0])

du = 0.0001
global U #measurement noise covariance
U = np.array([[du],[du],[du],[du],[du],[du]])

global Y #measurement
Y = np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float)
yshape = Y.shape
global H #measurement matrix
H = np.eye(yshape[0])

global R #measurement covariance
R = np.eye(yshape[0])

global angles
angles = (0,0,0)

global anglesold
anglesold = (0,0,0)



#generate forward velocity
scroll = vizact.move(0,0,-1*beltspeed,walktime)

#start the movements
walkway.add(scroll)
grass1.add(scroll)
grass2.add(scroll)
grass3.add(scroll)
divider.add(scroll)
for x in range(1,int((walkdistance*50)/(targetSL*2)),1):
	rt["T{0}".format(x)].add(scroll)
	lt["T{0}".format(x)].add(scroll)
	

def InverseK(vmat):
	global RdU0
	global RhmdU0

	S = np.matrix([[1,0,0],[0,1,0],[0,0,-1]],dtype=np.float)
	Rvv = np.matrix([[-1,0,0],[0,0,1],[0,1,0]],dtype=np.float)
	
	RdUt = vmat*RhmdU0.transpose()*RdU0
	
	RdUt = S*RdUt*S #make it left handed
	
	#do a matrix conditioning check, seems some degrees of freedom are colluded
#	determ = np.linalg.det(RdUt)
#	print('Rotation Matrix Determinant: ',determ)
#	print('R*Rt: ',RdUt*RdUt.transpose())

	#left handed sequences
	#X-Y-Z
#	beta = math.atan2(-RdUt[0,2],math.sqrt(RdUt[0,0]**2+RdUt[0,1]**2))
#	alpha = math.atan2(RdUt[1,2]/math.cos(beta),RdUt[2,2]/math.cos(beta))
#	gamma = math.atan2(RdUt[0,1]/math.cos(beta),RdUt[0,0]/math.cos(beta))
	
	#Z-Y-X #This works 3/22/2016
	beta = math.atan2(RdUt[2,0],math.sqrt(RdUt[2,1]**2+RdUt[2,2]**2))
	alpha = math.atan2(-1*RdUt[2,1]/math.cos(beta),RdUt[2,2]/math.cos(beta))
	gamma = math.atan2(-1*RdUt[0,1]/math.cos(beta),RdUt[0,0]/math.cos(beta))
	
	#Y-Z-X
	
	#Y-X-Z
	
	
	return(alpha,beta,gamma)
	
def kf_predict(X,P,A,Q,B,U):
	X = np.dot(A, X) + np.dot(B, U)
	P = np.dot(A, np.dot(P, A.T)) + Q
	return(X,P) 
	
def gauss_pdf(X, M, S):
	mshape = M.shape
	xshape = X.shape
	if mshape[1] == 1:
		DX = X - np.tile(M, xshape[1])
		E = 0.5 * np.sum(DX * (np.dot(np.linalg.inv(S), DX)), axis=0)
		E = E + 0.5 * mshape[0] * np.log(2 * np.pi) + 0.5 * np.log(np.linalg.det(S))
		P = np.exp(-E)
		np
	elif xshape[1] == 1:
		DX = tile(X, mshape[1])- M
		E = 0.5 * np.sum(DX * (np.dot(np.linalg.inv(S), DX)), axis=0)
		E = E + 0.5 * mshape[0] * np.log(2 * np.pi) + 0.5 * np.log(np.linalg.det(S))
		P = np.exp(-E)
	else:
		DX = X-M
		E = 0.5 * np.dot(DX.T, np.dot(np.linalg.inv(S), DX))
		E = E + 0.5 * mshape[0] * np.log(2 * np.pi) + 0.5 * np.log(np.linalg.det(S))
		P = np.exp(-E)
#	print('types: ')
#	print(type(P))
#	print(type(E))
	
	return (P[0],E[0]) 

def kf_update(X,P,Y,H,R):
	IM = np.dot(H, X)
	IS = R + np.dot(H, np.dot(P, H.T))
	K = np.dot(P, np.dot(H.T, np.linalg.inv(IS)))
	X = X + np.dot(K, (Y-IM))
	P = P - np.dot(K, np.dot(IS, K.T))
	LH = gauss_pdf(Y, IM, IS)
	return (X,P,K,IM,IS,LH) 
	
def UpdateViz(root,q,savestring,q3):#,speedlist,qq,savestring,q3):
	
	while not endflag.isSet():
		
		global rmark
		global lmark
		global viewLink
		global alphastack
		global betastack
		global gammastack
		global xstack
		global ystack
		global zstack
		global navigationNode
		global viconmat
		global X
		global P
		global A
		global Q
		global B
		global U
		global Y
		global H
		global R
		global angles
		global anglesold
		
		
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
		
		#HMD markers
		HMDX = float(data["HMDp"][0])/1000
		HMDY = float(data["HMDp"][1])/1000
		HMDZ = float(data["HMDp"][2])/1000
		#HMD rotation matrix
		for f in range(0,3,1):
			viconmat[0,f] = float(data["HMDm1"][f])
		for f in range(0,3,1):
			viconmat[1,f] = float(data["HMDm2"][f])
		for f in range(0,3,1):
			viconmat[2,f] = float(data["HMDm3"][f])

		angles = InverseK(viconmat)
		
		#check for large discontinuities in yaw and try to correct
		if (angles[2]-anglesold[2] >3):
			angles = (angles[0],angles[1],angles[2]-2*math.pi) #this will prevent yaw angle from crossing zero when redundant 0/360
		
		
		alphastack.append(np.array(angles[0],dtype=float))
		alphastack.pop(0)
		betastack.append(np.array(angles[1],dtype=float))
		betastack.pop(0)
		gammastack.append(np.array(angles[2],dtype=float))
		gammastack.pop(0)
		xstack.append(np.mean(np.array([HMDX],dtype=float)))
		xstack.pop(0)
		ystack.append(np.mean(np.array([HMDY],dtype=float)))
		ystack.pop(0)
		zstack.append(np.mean(np.array([HMDZ],dtype=float)))
		zstack.pop(0)
		
		#update measurement vector Y
		for z in range(0,3,1):
			Y.itemset(z,angles[z])#current angles
			Y.itemset(z+3,angles[z]-anglesold[z])#current angular velocity
		
		#kalman filter
		(X,P) = kf_predict(X,P,A,Q,B,U)
		(X,P,K,IM,IS,LH) = kf_update(X,P,Y,H,R)
		
		#update display
#		navigationNode.setEuler(-1*np.mean(gammastack)*180/math.pi,np.mean(alphastack)*180/math.pi,np.mean(betastack)*180/math.pi)#moving average filter
#		navigationNode.setEuler(-1*angles[2]*180/math.pi,angles[0]*180/math.pi,angles[1]*180/math.pi)#unfiltered
		navigationNode.setEuler(-1*float(X[2])*180/math.pi,float(X[0])*180/math.pi,float(X[1])*180/math.pi)#kalman filtered
		navigationNode.setPosition([-1*np.mean(xstack),np.mean(zstack),-1*np.mean(ystack)])

		rmark.setPosition(-1*RANKX,RANKZ-0.05,-1*RANKY)
		lmark.setPosition(-1*LANKX,LANKZ-0.05,-1*LANKY)
		
		anglesold = angles #update for next frame
		
		savestring = [FN,Rz,Lz,angles[0],angles[1],angles[2],float(X[0]),float(X[1]),float(X[2]),np.mean(alphastack),np.mean(betastack),np.mean(gammastack)]
		q3.put(savestring)
		
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

def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'ScrollingSteps_rev6.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
#	json.dump(['FrameNumber','Rfz','Lfz','RHIPy','LHIPy','RANky','LANKy','fastSLASYM','slowSLASYM','RHS','LHS'],file)
	json.dump(['FrameNumber','Rfz','Lfz','Pitch','Roll','Yaw','kpitch','kroll','kyaw','mpitch','mroll','myaw'],file)
	file.close()
	
	
	
	file = open(mststring,'a')#reopen for appending only
	while not endflag.isSet():
		savestring = q3.get()#look in the queue for data to write
	
		if savestring is None:
			continue
		else:
			json.dump(savestring, file)
	print("savedata stop flag raised, finishing...")
	while 1:
		try:
			savestring = q3.get(False,2)
		except:
			savestring = 'g'
#		print(savestring)
		if savestring  == 'g':
			break
			print("data finished write to file")
		else:
			json.dump(savestring, file)
			print("data still writing to file")
		
	print("savedata finished writing")
	file.close()
	
	
endflag = threading.Event()#an event to raise when we are ready to stop recording
def raisestop(sign):
	#the sign passed in doesn't do anything, I just didn't know how to make this work without passing something in...
	print("stop flag raised")
	endflag.set()
	t1.join(5)
	t2.join(5)
	t4.join(5)
	viz.quit()
	
root = ''#empty string
savestring = ''
#speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,savestring,q3))#,speedlist,qq,savestring,q3))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	