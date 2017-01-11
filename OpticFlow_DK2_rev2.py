#Endless flowing corridor to provide optic flow at a desired pre-programmed speed
#
#
#V2P DK2 R2
#
#Rev 2 loads optic flow objects from a pre-made file which can be altered, contains 5000 cooridnates for shapes
#
#WDA 12/5/2016

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
import csv
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
import vizfx.postprocess
import os

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe"')
time.sleep(2)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')


viz.go(
#viz.FULLSCREEN #run world in full screen
)

monoWindow = viz.addWindow(size=(1,1), pos=(0,1), scene=viz.addScene())
monoQuad = viz.addTexQuad(parent=viz.ORTHO, scene=monoWindow)
monoQuad.setBoxTransform(viz.BOX_ENABLED)
monoQuad.setTexQuadDisplayMode(viz.TEXQUAD_FILL)
texture = vizfx.postprocess.getEffectManager().getColorTexture()

def UpdateTexture():
    monoQuad.texture(texture)
vizact.onupdate(0, UpdateTexture)

global hmd
# Setup Oculus Rift HMD
hmd = oculus.Rift()
#if not hmd.getSensor():
#	sys.exit('Oculus Rift not detected')
#else:
#	profile = hmd.getProfile()
#	hmd.setIPD(profile.ipd)

global sensei
sensei = hmd.getSensor()
profile = hmd.getProfile()
hmd.setIPD(profile.ipd)
	
# Setup navigation node and link to main view
global navigationNode
navigationNode = viz.addGroup()
global viewLink
viewLink = viz.link(navigationNode, viz.MainView)

global beltspeed
beltspeed = 1 #units must be meters/second

#hmrl = viz.addChild('HMRL8.osgb')
#hmrl.setPosition(0,0,0)
#hmrl.setEuler(90,270,0)
#hmrl.setScale(0.01,0.01,0.01)
global shapes
shapes = []

#create optic flow
if os.path.isfile('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\OpticFlow1.txt'):
	f = open('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\OpticFlow1.txt','r')
	x = f.readline()
	x = x.replace('\n','')
	x = x.split(',')
	for n in range(len(x)):
		x[n] = float(x[n])
	y = f.readline()
	y = y.replace('\n','')
	y = y.split(',')
	for n in range(len(y)):
		y[n] = float(y[n])
	z = f.readline()
	z = z.replace('\n','')
	z = z.split(',')
	for n in range(len(z)):
		z[n] = float(z[n])
	f.close()
#	print(type(x[0]))
#	print(y)
#	print(z)
	for n in range(len(x)):
		shape = vizshape.addSphere(0.1,10,10)
		shape.setPosition([x[n],y[n],z[n]])
		shape.color(1,1,1)
		shapes.append(shape)
	
else:
	print('Error file containing coordinated for flow not found...')



#generate forward velocity
#scroll = vizact.move(0,0,-1*beltspeed,50)
#for x in range(1,50,1):
#	rt["T{0}".format(x)].add(scroll)
#	r2t["T{0}".format(x)].add(scroll)
#	r3t["T{0}".format(x)].add(scroll)
#	r4t["T{0}".format(x)].add(scroll)
#	r5t["T{0}".format(x)].add(scroll)
#	r6t["T{0}".format(x)].add(scroll)
#	r7t["T{0}".format(x)].add(scroll)
#	r8t["T{0}".format(x)].add(scroll)
	
global HideSphere #for trying to block the view when IK freaks out or too many markers are occluded
HideSphere = viz.addChild('hidesphere2.osgb',scale=[0.1,0.1,0.1])
HideSphere.setPosition(0,0,0)
HideSphere.color(0,0,0)
HideSphere.visible(0)

#setup rotation matrix for constant transform between headset and looking forward
a0 = -8.57*math.pi/180
b0 = 86.417*math.pi/180
g0 = -11.31*math.pi/180

#ha0 = 95*math.pi/180#orientation of hand cluster at zero
#hb0 = 78*math.pi/180
#hg0 = -95.7*math.pi/180
ha0 = 95*math.pi/180#orientation of hand cluster at zero
hb0 = 78*math.pi/180
hg0 = 95.7*math.pi/180

#for the HMD
Ra0 = np.matrix([[1,0,0],[0, float(math.cos(a0)), float(-1*math.sin(a0))],[0,float(math.sin(a0)),float(math.cos(a0))]],dtype=np.float)
Rb0 = np.matrix([[math.cos(b0),0,math.sin(b0)],[0,1,0],[-1*math.sin(b0),0,math.cos(b0)]],dtype=np.float)
Rg0 = np.matrix([[math.cos(g0),-1*math.sin(g0),0],[math.sin(g0),math.cos(g0),0],[0,0,1]],dtype=np.float)
#for the HAND cluster
Rha0 = np.matrix([[1,0,0],[0, float(math.cos(ha0)), float(-1*math.sin(ha0))],[0,float(math.sin(ha0)),float(math.cos(ha0))]],dtype=np.float)
Rhb0 = np.matrix([[math.cos(hb0),0,math.sin(hb0)],[0,1,0],[-1*math.sin(hb0),0,math.cos(hb0)]],dtype=np.float)
Rhg0 = np.matrix([[math.cos(hg0),-1*math.sin(hg0),0],[math.sin(hg0),math.cos(hg0),0],[0,0,1]],dtype=np.float)

global Ph0 #for hmd
#Ph0 = np.array([[.05567],[.099],[-0.007736]])#this is the location of the view point in the HMD frame of reference
#Ph0 = np.array([[.0259],[.142],[0]])#this is the location of the view point in the HMD frame of reference
Ph0 = np.array([[0.05],[.155],[0]])

global Phand0
Phand0 = np.array([[0],[0],[-0.03]])

global RhmdU0 #for hmd
RhmdU0 = Rg0*Rb0*Ra0 

global RhandU0 #for the glove
RhandU0 = Rhg0*Rhb0*Rha0

global RdU0
RdU0 = np.matrix([[1,0,0],[0,1,0],[0,0,1]],dtype=np.float)

global viconmat #for the HMD
viconmat = np.matrix([[0,0,0],[0,0,0],[0,0,0]],dtype=np.float)

global handmat #for the hand cluster
handmat = np.matrix([[0,0,0],[0,0,0],[0,0,0]],dtype=np.float)

global X #k-1 timestep state estimate initiated as zeros
X = np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float)

global Xpre
Xpre = np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float)

global P #state coavariance prediction
P = np.diag((0.01,0.01,0.01,0.01,0.01,0.01))
#print(P)

global Ppre
Ppre = np.diag((0.01,0.01,0.01,0.01,0.01,0.01))

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

def InverseK(vmat,hx,hy,hz,RdU0,RhmdU0,Ph0):
#	global RdU0
#	global RhmdU0
#	global Ph0

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
	
	
#	print(Pht)
	
	return(alpha,beta,gamma,Pht[0],Pht[1],Pht[2])#return the orientation and position data
	
def CheckIK(vmat,xp,yp,zp,x,y,z,markernum):
#	print('vmat',vmat)
#	print('x,y,z',x,y,z)
	HMTM = np.matrix([[vmat[0,0],vmat[0,1],vmat[0,2],xp],[vmat[1,0],vmat[1,1],vmat[1,2],yp],[vmat[2,0],vmat[2,1],vmat[2,2],zp],[0,0,0,1]])
#	print('HMTM',HMTM)

	if np.linalg.cond(HMTM) < 1/sys.float_info.epsilon:
		HMTMi = np.linalg.inv(HMTM)
	else:
		#handle it
		flag = 1
#		print('warning, singular transformation detected')
		return [9999,9999,9999,flag]
	
#	print('HMTMi',HMTMi)
	vec = np.matrix([[x],[y],[z],[1]])
#	print('vec',vec)
	
	ans = HMTMi * vec
	flag = 0
	#examine whether each marker is labelled correctly
	if markernum==1:
		if (abs(ans[0]) < 0.0006) | (abs(ans[1]) < 0.0006) | (abs(0.0002-ans[2]) < 0.0002):
			flag = 0
		else:
			flag = 1
	elif markernum == 2:
		if (abs(ans[0]) < 0.002) | (abs(ans[1]) < 0.001) | (abs(-0.037-ans[2]) < 0.0003):
			flag = 0
		else:
			flag = 1
	elif markernum == 3:
		if (abs(ans[0]) < 0.001) | (abs(0.0281-ans[1]) < 0.0005) | (abs(0.07-ans[2]) < 0.0005):
			flag = 0
		else:
			flag = 1
		

	vargout = [ans.item(0,0),ans.item(1,0),ans.item(2,0),flag]
	return vargout #return 4 elements, 3 are x y z in local coordinates and the fourth is a flag
	
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

np.set_printoptions(precision=4)
global hideflag
hideflag = 0

global yawoff
yawoff = 0
global pitchoff
pitchoff = 0
global rolloff
rolloff = 0

global check 
check = {}
check["HMD1"] = 0
check["HMD2"] = 0
check["HMD3"] = 0
	
def UpdateViz(root,q,savestring,q3):#,speedlist,qq,savestring,q3):
	
	while not endflag.isSet():
		
		global rmark
		global lmark
		global rmark2
		global lmark2
		global viewLink
		global navigationNode
		global X
		global P
		global A
		global Q
		global B
		global U
		global Y
		global H
		global R
		global Xpre
		global Ppre
		global angles
		global anglesold
		global viconmat
		global hideflag
		global HideSphere
		global Ph0
		global Phand0
		global RdU0
		global RhmdU0
		global Ph0
		global RhandU0
		global handmat
		global GLOVE
		global sensei
		global check
		
		
		root = q.get()
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
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

		IKdata = InverseK(viconmat,HMDX,HMDY,HMDZ,RdU0,RhmdU0,Ph0)
		
		if (IKdata[2]-anglesold[2] >3):
			IKdata = (IKdata[0],IKdata[1],IKdata[2]-2*math.pi,IKdata[3],IKdata[4],IKdata[5]) #this will prevent yaw angle from crossing zero when redundant 0/360
		
		#update measurement vector Y
		for z in range(0,3,1):
			Y.itemset(z,IKdata[z])#current angles
#			Y.itemset(z+3,IKdata[z]-anglesold[z])#current angular velocity
			Y.itemset(z+3,IKdata[z+3])
		
		#kalman filter
		(Xpre,Ppre) = kf_predict(X,P,A,Q,B,U)
		(X,P,K,IM,IS,LH) = kf_update(Xpre,Ppre,Y,H,R)
		
		for f in range(1,4,1): #check the 7 HMD markers to see if they are labelled correctly
			tempx = float(data["HMD{}".format(f)][0])/1000
			tempy = float(data["HMD{}".format(f)][1])/1000
			tempz = float(data["HMD{}".format(f)][2])/1000
			check["HMD{}".format(f)]= CheckIK(viconmat,HMDX,HMDY,HMDZ,tempx,tempy,tempz,f)
#			print(check)
		
		HideSphere.setPosition(-1*float(X[3]),float(X[5]),-1*float(X[4]))
		if (check["HMD1"][3] == 1) |(check["HMD2"][3] == 1) | (check["HMD3"][3] == 1):
			HideSphere.visible(1)
		else:
			HideSphere.visible(0)
		
		
		
		navigationNode.setEuler(-1*float(X[2])*180/math.pi,float(X[0])*180/math.pi,float(X[1])*180/math.pi)#kalman filtered
		navigationNode.setPosition([-1*float(X[3]),float(X[5]),-1*float(X[4])])
		
		anglesold = IKdata #update for next frame
		
		savestring = [FN,Rz,Lz]
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
	mststring = str(mst2)+'OpticFlow_DK2_rev2.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz'])
	file.close()
	
	file = open(mststring,'a')#reopen for appending only
	csvw = csv.writer(file)
	while not endflag.isSet():
		savestring = q3.get()#look in the queue for data to write
	
		if savestring is None:
			continue
		else:
			csvw.writerow(savestring)
	print("savedata stop flag raised, finishing...")
	while 1:
		try:
			savestring = q3.get(False,2)
		except:
			savestring = 'g'
		if savestring  == 'g':
			break
			print("data finished write to file")
		else:
			csvw.writerow(savestring)
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
	