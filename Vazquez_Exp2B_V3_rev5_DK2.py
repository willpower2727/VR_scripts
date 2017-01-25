#Exp2B V3 alteration of "Perceptual Sensory Correlates of Split Belt Walking Adaptation"
#2 steps
#
#Subjects perform 30 stepping trials on each leg, they try to match anterior hip-ankle distance at HS with the left or "slow" leg HS. 
#targets are displayed on a latitudinal grid, 20 targets, 2 cm apart. The left leg target appears as a red circle.The legs start tied, 
#the subject takes a step, then the treadmill moves that foot back to the original pose.
#
#V3 is training with biofeedback on both sides
#
#rev updates the orientation and position with marker data
#
#V2P_DK2_R2
#
#William Anderton 3/29/2016

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
import imp
oculus = imp.load_source('oculus', 'C:\Program Files\WorldViz\Vizard5\python\oculus.py')
import vizlens
import pykalman

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe")
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
viz.go(
#viz.FULLSCREEN #run world in full screen
)
#time.sleep(2)#show off our cool logo, not really required but cool

global hmd
hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')
else:
	profile = hmd.getProfile()
	if profile:
		hmd.setIPD(profile.ipd)

# Setup navigation node and link to main view
global navigationNode
navigationNode = viz.addGroup()
global viewLink
viewLink = viz.link(navigationNode, viz.MainView)

global messagewin
messagewin = viz.addText('MOVING',pos=[0,0.1,0],scale=[0.1,0.1,0.1])
messagewin.color(0,0,0)

global targetL
targetL = 0.4

global targetR
targetR = targetL

global targettol
targettol = 0.02

'''
	global circleL #slow leg circle marker
	circleL = vizshape.addSphere(0.01,50,50,color=viz.RED)
	circleL.setPosition(-0.03,targetL,0)
	circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

	global circleR #slow leg circle marker
	circleR = vizshape.addSphere(0.01,50,50)
	circleR.color(1,0.7,0)
	circleR.setPosition(0.04,targetR,0)
	circleR.disable(viz.LIGHTING)#no shading, we don't want depth perception here

	prompt bars
	global neutralR
	neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.05,0.0125,0.0125], cache=viz.CACHE_NONE)
	neutralR.setPosition([0.06,-0.02,0])
	neutralR.disable(viz.LIGHTING)

	global neutralL
	neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.05,0.0125,0.0125], cache=viz.CACHE_NONE)
	neutralL.setPosition([-0.05,-0.02,0])
	neutralL.disable(viz.LIGHTING)

	global fineR
	fineR = vizshape.addSphere(0.04,50,50,color=viz.RED)
	fineR.setPosition(-0.1,targetL,-0.25)
	fineR.disable(viz.LIGHTING)
'''

#create latitudinal grid
lines = {}#create empty dictionary
for x in range(1,27,1):
	lines["T{0}".format(x)]=vizshape.addBox(size=[0.835,0.004,0.006])
	lines["T{0}".format(x)].setPosition(0.462,0.001,-1.45+(x-1)*0.05)
	lines["T{0}".format(x)].color(0.1,0,0.1)
	lines["T{0}".format(x)].disable(viz.LIGHTING)
	#	print((x-1)*0.02)
'''
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
'''	

#viz.MainView.setPosition(0, 0.25, -0.55)
#viz.MainView.setEuler(0,0,0)

global histzR
histzR = -500
global histzL
histzL = -500

global rgorb
rgorb = 0
global lgorb
lgorb = 0

global Rerror
Rerror = 0
global Lerror
Lerror = 0

global RHS
RHS = 0
global LHS
LHS = 0

global phase
phase = 0

#initialize the order of tests, for now, only the right side will be tested
global STEPNUM
STEPNUM =15
#setup array of randomly picked steps
global randy
randy = [2,1] * STEPNUM
'''
	order = [1,2] * STEPNUM#change this line to add in left tests
	while len(randy) < 10:#optimistically sample the solution space for test orders
		random.shuffle(order)
		if order in randy:
			continue
		if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
			randy.append(order[:])
	randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
	print(randy)
'''

sky = viz.addChild('sky_day.osgb')
grass1 = viz.addChild('ground_grass.osgb')
grass1.setPosition(0,-0.01,0)

#create a divider line
global divider
divider = vizshape.addQuad(size=(0.01,1.625),
	axis=-vizshape.AXIS_Y,
	cullFace=False,
	cornerRadius=0)
divider.setPosition(0.462,0.001,0.0125-1.625/2)
divider.color(255,255,255)

global walkway
walkway = viz.addChild('ground.osgb',scale = [0.0167,1,1.625/50])
walkway.setPosition(0.462,0,0.0125-1.625/2)#start at one end of the walkway

#targets
global boxR
boxR = vizshape.addBox(size=[0.25,0.008,2*targettol])
boxR.setPosition(0.462+0.2,0.011,-1*(1.45-targetR))
boxR.color(0.1,0.1,0.1)
boxR.disable(viz.LIGHTING)
global boxL
boxL = vizshape.addBox(size=[0.25,0.008,2*targettol])
boxL.setPosition(0.462-0.2,0.011,-1*(1.45-targetL))
boxL.color(0.1,0.1,0.1)
boxL.disable(viz.LIGHTING)

global HistBallR
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.3,0.01,0.01], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.462+0.2,0.001,-1.45])
HistBallR.setEuler(180,0,0)
HistBallR.color(1,204/255,51/255)
#HistBallR.alpha(0.8)
HistBallR.disable(viz.LIGHTING)

global HistBallL
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.3,0.01,0.01], cache=viz.CACHE_NONE)
HistBallL.setPosition([0.462-0.2,0.001,-1.45])
#HistBallL.alpha(0.8)
HistBallL.color(1,204/255,51/255)
HistBallL.disable(viz.LIGHTING)

'''
def updatetargetdisplay(ts,vizobj,flag,flag2):  #distance value, circle object, flag=1 for left, anything else for right
	#flag2 signifies if the highlighted number needs to change
	
	global tnums
#	print(tnums)
	#figure out which target to place circle in and highlight the number
#	ts = abs(ts)*100 #convert units to centimeters for rounding
	ts = ts*100
#	print("ts",ts)
	oddnum = np.floor(ts / 2.) * 2 + 1 #round to the nearest odd integer
#	print("oddnum",int(oddnum)/100)
	index = int((oddnum-1)/2)
#	print("index",index)
	if (flag2 == 1):
		#turn the other target numbers back to white
		for i in [x for x in xrange(21) if x != int(index)]:
			tnums["Num{0}".format(i)].color(viz.WHITE)
		#highlight the selected target
		try:
			tnums["Num{0}".format(int(index))].color(viz.RED)
		except:
			pass
	else:
		pass
	
	#update position of circle
#	vizobj.setPosition(-0.1,oddnum/100,0)
	if (flag == 1):
		vizobj.setPosition(-0.03,ts/100,0) #analog placement
#		vizobj.setPosition(-0.03,oddnum/100,0)#discrete placement
	else:
		vizobj.setPosition(0.04,ts/100,0) #analog placement
#		vizobj.setPosition(0.04,oddnum/100,0) #discrete placement
		
	return index #return in units of meters
'''
	
#global targetnum
#targetnum = updatetargetdisplay(targetL,circleL,1,1)
#nothing = updatetargetdisplay(targetR,circleR,2,2)

#circleL.visible(0)#turn off markers
#circleR.visible(0)

global Rgamma
Rgamma = 0
global Lgamma
Lgamma = 0

global Rspeed
Rspeed = 0
global Lspeed
Lspeed = 0

global old0
old0 = 0
global old1
old1 = 0

global stepind #this keeps track of the total # of attempts
stepind = 0

global accum 
accum = 0

#for smoothing position/orientation tracking
#global alphastack
#alphastack = [0] * 5
#global betastack
#betastack = [0] * 5
#global gammastack
#gammastack = [0] * 5
#global xstack
#xstack = [0] * 5
#global ystack
#ystack = [0] * 5
#global zstack
#zstack = [0] * 5

#create foot squares
global rmark
rmark = vizshape.addBox(size=(.025,.025,.025))
rmark.color(255,0,0)
rmark.setPosition(0,0,0)
rmark.disable(viz.LIGHTING)

global lmark
lmark = vizshape.addBox(size=(.025,.025,.025))
lmark.color(0,255,0)
lmark.setPosition(0,0,0)
lmark.disable(viz.LIGHTING)

#setup rotation matrix for constant transform between headset and looking forward
#a0 = -8.57*math.pi/180
#b0 = 86.417*math.pi/180
#g0 = -11.31*math.pi/180
a0 = -11.6*math.pi/180
b0 = 83.5*math.pi/180
g0 = -10.3*math.pi/180

Ra0 = np.matrix([[1,0,0],[0, float(math.cos(a0)), float(-1*math.sin(a0))],[0,float(math.sin(a0)),float(math.cos(a0))]],dtype=np.float)
Rb0 = np.matrix([[math.cos(b0),0,math.sin(b0)],[0,1,0],[-1*math.sin(b0),0,math.cos(b0)]],dtype=np.float)
Rg0 = np.matrix([[math.cos(g0),-1*math.sin(g0),0],[math.sin(g0),math.cos(g0),0],[0,0,1]],dtype=np.float)

global Ph0 
Ph0 = np.array([[.05567],[.099],[-0.007736]])#this is the location of the view point in the HMD frame of reference

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
#A = np.array([[1,0,0,dt,0,0],[0,1,0,0,dt,0],[0,0,1,0,0,dt],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]],dtype=np.float)
A = np.eye(6,dtype=np.float)

xshape = X.shape
dq = 0.35
dqq = 0.5
global Q #process noise covariance
#Q = np.eye(xshape[0])
Q = np.array([[dq,0,0,0,0,0],[0,dq,0,0,0,0],[0,0,dq,0,0,0],[0,0,0,dqq,0,0],[0,0,0,0,dqq,0],[0,0,0,0,0,dqq]],dtype=np.float)

global B #system input matrix
B = np.eye(xshape[0])

du = 0.0001
duu = 0.0001
global U #measurement noise covariance
U = np.array([[du],[du],[du],[duu],[duu],[duu]])

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

def InverseK(vmat,hx,hy,hz):
	global RdU0
	global RhmdU0
	global Ph0

	S = np.matrix([[1,0,0],[0,1,0],[0,0,-1]],dtype=np.float)
	Rvv = np.matrix([[-1,0,0],[0,0,1],[0,1,0]],dtype=np.float)
	
	RdUtr = vmat*RhmdU0.transpose()*RdU0
	RdUt = S*RdUtr*S #make it left handed	
	
	#Z-Y-X #This works 3/22/2016
	beta = math.atan2(RdUt[2,0],math.sqrt(RdUt[2,1]**2+RdUt[2,2]**2))
	alpha = math.atan2(-1*RdUt[2,1]/math.cos(beta),RdUt[2,2]/math.cos(beta))
	gamma = math.atan2(-1*RdUt[0,1]/math.cos(beta),RdUt[0,0]/math.cos(beta))
	
	#homogeneous trasnformation of the HMD, used to compute where the true view position should be
	HhmdUt = np.matrix([[RdUtr[0,0],RdUtr[0,1],RdUtr[0,2],hx],[RdUtr[1,0],RdUtr[1,1],RdUtr[1,2],hy],[RdUtr[2,0],RdUtr[2,1],RdUtr[2,2],hz],[0,0,0,1]])
	Pht = HhmdUt*np.array([[Ph0[0]],[Ph0[1]],[Ph0[2]],[1]])
	
	return(alpha,beta,gamma,Pht[0],Pht[1],Pht[2])

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



def UpdateViz(root,q,speedlist,qq,savestring,q3):

	global histzL
	global histzR
	global targetL
	global targetR
	global circleL
	global circleR
	global rgorb
	global lgorb
	global cpps
	global Rerror
	global Lerror
	global targetnum
	global targettol
	global RHS
	global LHS
	global phase
	global Rgamma
	global Lgamma
	global Rspeed
	global Lspeed
	global neutralR
	global neutralL
	global stepind
	global messagewin
	global accum
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
	global viconmat
	global navigationNode
	global HistBallL
	global HistBallR
	
	
	while not endflag.isSet():
		root = q.get()#look for the next frame data in the thread queue
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

		IKdata = InverseK(viconmat,HMDX,HMDY,HMDZ)
		
		#check for large discontinuities in yaw and try to correct
		if (IKdata[2]-anglesold[2] >3):
			IKdata = (IKdata[0],IKdata[1],IKdata[2]-2*math.pi,IKdata[3],IKdata[4],IKdata[5]) #this will prevent yaw angle from crossing zero when redundant 0/360
		
#		xstack.append(np.mean(np.array([HMDX],dtype=float)))
#		xstack.pop(0)
#		ystack.append(np.mean(np.array([HMDY],dtype=float)))
#		ystack.pop(0)
#		zstack.append(np.mean(np.array([HMDZ],dtype=float)))
#		zstack.pop(0)
		
		#update measurement vector Y
		for z in range(0,3,1):
			Y.itemset(z,IKdata[z])#current angles
			Y.itemset(z+3,IKdata[z+3])#current position
			
		#kalman filter
		(X,P) = kf_predict(X,P,A,Q,B,U)
		(X,P,K,IM,IS,LH) = kf_update(X,P,Y,H,R)
		
		navigationNode.setEuler(-1*float(X[2])*180/math.pi,float(X[0])*180/math.pi,float(X[1])*180/math.pi)#kalman filtered
		navigationNode.setPosition([-1*float(X[3]),float(X[5]),-1*float(X[4])-1])
		
		
#		print("RANKY",RANKY)
		rmark.setPosition(-1*RANKX,RANKZ-0.04,-1*RANKY)
		lmark.setPosition(-1*LANKX,LANKZ-0.04,-1*LANKY)

#		Ralpha = (RHIPY+LHIPY)/2-RANKY
#		Lalpha = (LHIPY+RHIPY)/2-LANKY
		Rgamma = LANKY-RANKY
		Lgamma = RANKY-LANKY
		
#		print('phase',phase)
		if (phase == 0):#move right leg
			messagewin.message('Moving...')
			if (Rz<-30) & (Lz<-30) & (abs(1.45-RANKY) >= 0.04):
				Rspeed = int(300*math.copysign(1,1.45-RANKY))
			elif (abs(1.45-RANKY) < 0.04):
				Rspeed = 0
#				circleR.visible(0)#hide the circles
#				circleL.visible(0)
				phase = 1#move on to the next 
			else:
				Rspeed = 0#subject is stumbling? sto
		elif (phase == 1):#move left leg
			messagewin.message('Moving...')
			if (Rz<-30) & (Lz<-30) & (abs(1.45-LANKY) >= 0.04):
				Lspeed = int(300*math.copysign(1,1.45-LANKY))
			elif (abs(1.45-LANKY) < 0.04):
				Lspeed = 0
				phase = 2
			else:
				Lspeed = 0#subject is stumbling? stop
		elif (phase == 2):#prompt which side to do next
			messagewin.message('Please match feet position.')	
			messagewin.visible(1)
			HistBallL.visible(0)
			HistBallR.visible(0)
#			for i in [x for x in xrange(21) if x != int(index)]:
#				tnums["Num{0}".format(i)].color(viz.WHITE)
			if (abs(RANKY-LANKY)<0.01) & (Rz<-100) & (Lz<-100):
				rmark.visible(1)
				lmark.visible(1)
#				circleR.visible(1)
#				circleL.visible(1)
#				nothing = updatetargetdisplay(LANKY-RANKY,circleR,2,2)
#				nothing = updatetargetdisplay(RANKY-LANKY,circleL,1,2)
				if (accum >= 120):
					messagewin.visible(0)#turn it off when done
	#				messagewin.message(str(abs(RANKY-LANKY)))
					boxR.color(0.1,0.1,0.1)
					boxL.color(0.1,0.1,0.1)
#					rmark.visible(0)
#					lmark.visible(0)
#					circleR.visible(0)
#					circleL.visible(0)
					try:
						if (randy[stepind] == 1):#right side next
							boxR.setPosition(0.462+0.2,0.011,-1*(1.45-targetL))
							boxR.visible(1)
							boxL.visible(0)
							pass
						else:
							boxR.visible(0)
							boxL.visible(1)
							
						phase = 3
						accum = 0
					except:
						#out of steps
						phase = 4
				else:
					messagewin.message('Please hold still.')	
					print(accum)
					accum = accum+1
			else:
				pass
#				circleR.visible(1)
#				circleL.visible(1)
#				nothing = updatetargetdisplay(LANKY-RANKY,circleR,2,2)
#				nothing = updatetargetdisplay(RANKY-LANKY,circleL,1,2)
		elif (phase == 3):#wait for steps
			#gait events
			if (Rz <= -30) & (histzR > -30):#RHS
				stepind = stepind+1
				Rerror = targetL-Rgamma
				RHS = 1
				HistBallR.setPosition(0.462+0.2,0.011,-1*(1.45-Rgamma))
				HistBallR.visible(1)
				if (abs(Rerror) < targettol):
					rgorb = 1
					boxR.color(0,1,0)
				else:
					rgorb = 0
					boxR.color(1,0,0)
#				nothing = updatetargetdisplay(Ralpha,circleR,2,2)
#				circleR.visible(1)
#				neutralR.visible(0)
#				neutralL.visible(0)
				phase = 0#continue
			else:
				RHS = 0
				
			if (Lz <= -30) & (histzL > -30):#LHS
				stepind = stepind+1
				Lerror = targetL-Lgamma
				LHS = 1
				boxL.setPosition(0.462-0.2,0.011,-1*(1.45-Lgamma))
#				HistBallL.setPosition(0.462-0.2,0.001,-1*(1.45-Lgamma))
				if (abs(Lerror) < targettol):
					lgorb = 1
#					boxL.color(0,1,0)
				else:
					lgorb = 0
#					boxL.color(1,0,0)
#				targetnum = updatetargetdisplay(Lalpha,circleL,1,1)
#				circleL.visible(1)
#				neutralR.visible(0)
#				neutralL.visible(0)
#				targetSLOW = Lalpha
				phase = 0#continue
				targetL = Lgamma
			else:
				LHS = 0
		elif (phase == 4):
			messagewin.message('Test Complete!')
			messagewin.visible(1)
			if (RANKY-LANKY >= 0.04) & (Rz < -30) & (Lz < -30):
				Lspeed = int(300*math.copysign(1,(RANKY-LANKY)))
				Rspeed = 0
			elif (LANKY-RANKY >= 0.04) & (Rz < -30) & (Lz < -30):
				Rspeed = int(300*math.copysign(1,(LANKY-RANKY)))
				Lspeed = 0
			else:
				Rspeed = 0
				Lspeed = 0
#			break

		#send speed update
		speedlist = [Rspeed,Lspeed,2200,2200,0]#the accelerations "2200 mm/s^2" are not arbitrary.
		qq.put(speedlist)
		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,Rgamma,Lgamma,Rerror,Lerror,RANKY,LANKY]#organize the data to be written to file
		q3.put(savestring)
		
		
		
	#close cpp server
	cpps.kill()
		
		
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
		
#	print data
	return data

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
#		print(data)
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

def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'EXP2B_DK2_V3_rev5.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RGORB','LGORB','Rgamma','Lgamma','Rerror','Lerror','RANKY','LANKY'],file)
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

def sendtreadmillcommand(speedlist,qq):
	
	HOST2 = 'BIOE-PC'
	PORT2 = 4000
	s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print 'Treadmill Socket created'
	print 'Treadmill Socket now connecting'
	s2.connect((HOST2,PORT2))
	
	def serializepacket(speedR,speedL,accR,accL,theta):
		fmtpack = struct.Struct('>B 18h 27B')#should be 64 bits in length to work properly
		outpack = fmtpack.pack(0,speedR,speedL,0,0,accR,accL,0,0,theta,~speedR,~speedL,~0,~0,~accR,~accL,~0,~0,~theta,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
		return(outpack)

	while not endflag.isSet():
		
		global old0
		global old1
		speedlist = qq.get()#doesn't block?
		if speedlist is None:
			continue #keep checking until there is something to send
		elif (speedlist[0] == old0) & (speedlist[1] ==old1):#if it's a repeat command, ignore it
			continue
		else:#speeds must be new and need to be updated
			out = serializepacket(speedlist[0],speedlist[1],speedlist[2],speedlist[3],speedlist[4])
			s2.send(out)
			old0 = speedlist[0]
			old1 = speedlist[1]
	#at the end make sure the treadmill is stopped
	out = serializepacket(0,0,500,500,0)
	s2.send(out)
	s2.close()
	
	
endflag = threading.Event()#an event to raise when we are ready to stop recording
def raisestop(sign):
	#the sign passed in doesn't do anything, I just didn't know how to make this work without passing something in...
	print("stop flag raised")
	endflag.set()
	t1.join(5)
	t2.join(5)
	t3.join(5)
	t4.join(5)
	viz.quit()

root = ''#empty string
savestring = ''
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq,savestring,q3))
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
#vizact.onkeydown('r',ReCenterView,hmd)#biggle is meaningless, just need to pass something into the raisestop callback
	














