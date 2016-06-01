#WDA 10/30/2015
#V2P DK2 R1
#lab demo of Vicon head tracking ability

import socket
import sys
import io
import re
#import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
import scipy
import numpy as np
import math
import oculus
#import vizmat
import vizlens

np.set_printoptions(precision=5)

#check vizard4/bin/vizconfig to change which monitor displays the VR window
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.go(
viz.FULLSCREEN 
)

time.sleep(2)#show off our cool logo, not really required but cool
global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor

viz.fov(110)
#pincushion = vizlens.PincushionDistortion()
#pincushion.setK1(0.2)

im = viz.addTexture('NYC2.jpg')
#im2 = viz.addTexture('NYC.jpg')


background = viz.addTexQuad()
background.setPosition(0,2,6)
background.setScale(21,7,1)
background.texture(im)

roof = viz.addTexQuad()
roof.setPosition(0.5,2.9,-4)
roof.setEuler(0,90,0)
roof.setScale(6,12,1)
#roof.texture(im2)

#sky = viz.addChild('sky_day.osgb')
#ground = viz.addChild('ground_grass.osgb')
#ground.setPosition(0,-0.25,0)
hmrl = viz.addChild('HMRL.osgb')
hmrl.setPosition(0,0,0)
hmrl.setEuler(90,270,0)
hmrl.setScale(0.01,0.01,0.01)

boxL = viz.addChild('ball.wrl',color=(0.063,0.102,0.898),scale=[0.25,0.25,0.25])

#male = viz.add('hand.cfg') 
#male.setPosition(0.5,0,-0.9)
#male.setEuler(180,0,0)

#male.state(2)
#armBone = male.getBone('Bip01 R Forearm') 
#armBone.lock() 
#armBone.setEuler(90, 0, 0)

global v1
global v2
global v3
global va
global M1
v1 = np.array([0,0,0],dtype=float)
v2 = np.array([0,0,0],dtype=float)
v3 = np.array([0,0,0],dtype=float)
va = np.array([0,0,0],dtype=float)
M1 = np.zeros((3,3),dtype=float)

global alphastack
alphastack = [0] * 20
global betastack
betastack = [0] * 20
global gammastack
gammastack = [0] * 20
global deltastack
deltastack = [0] * 20


def UpdateViz(root,q):

	while not endflag.isSet():
		global v1
		global v2
		global v3
		global va
		global M1
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
#		RANKY = float(data["RANK"][1])/1000
#		LANKY = float(data["LANK"][1])/1000
		pc1x = float(data["HMD1"][0])/1000
		pc1y = float(data["HMD1"][1])/1000
		pc1z = float(data["HMD1"][2])/1000
		
		pc2x = float(data["HMD2"][0])/1000
		pc2y = float(data["HMD2"][1])/1000
		pc2z = float(data["HMD2"][2])/1000
		
		pc3x = float(data["HMD3"][0])/1000
		pc3y = float(data["HMD3"][1])/1000
		pc3z = float(data["HMD3"][2])/1000
		
		v1[0] = pc1x-pc2x
		v1[1] = pc1y-pc2y
		v1[2] = pc1z-pc2z
		
		va[0] = pc3x-pc2x
		va[1] = pc3y-pc2y
		va[2] = pc3z-pc2z
		
		v2 = np.cross(v1,va)
		
#		v2[0] = pc1x-pc3x
#		v2[1] = pc1y-pc3y
#		v2[2] = pc1z-pc3z
		
		SetViewQuat(v1,v2)
#		viz.MainView.setPosition(-1*np.mean([pc1x,pc2x]),np.mean([pc1z,pc2z]),-1*np.mean([pc1y,pc2y]))
		viz.MainView.setPosition(-1*pc1x,pc1z,-1*pc1y)

		
#	print("data has all been gotten")

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
		data = s.recv(8)#receive the initial message
		data3 = data[:3]#get first 3 letters
		if (data3 == "New"):
			nextsizestring = data[3:]#get the integer after "New"
			nextsizestring2 = nextsizestring.rstrip('\0')#format
			nextsize = int(nextsizestring2,10)#cast as type int
#			print("Next Packet is size: ")
#			print(nextsize)
			s.send('b')#tell cpp server we are ready for the packet
			databuf = ''#initialize a buffer
			while (sys.getsizeof(databuf) < nextsize+21):
				data = s.recv(nextsize)#data buffer as a python string
				databuf = databuf + data#collect data into buffer until size is matched
			root = databuf
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
#			path = root.find("FrameNumber")
#			print(path.attrib)
			q.put(root)#place the etree into the threading queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()
#	q.join()
	
endflag = threading.Event()
def raisestop(sign):
	print("stop flag raised")
	endflag.set()
	t1.join()
	t2.join()
#	t4.join()
	viz.quit()

def SetViewQuat(vec1,vec2):
	global M1
	global alphastack
	global betastack
	global gammastack
	global deltastack
	
	vec1 = vec1 / np.linalg.norm(vec1)
	vec2 = vec2 / np.linalg.norm(vec2)
	
	vec3 = np.cross(vec1,vec2)
	
#	vec1 = np.divide(vec1,np.linalg.norm(vec1))
#	vec3 = np.divide(vec3,np.linalg.norm(vec3))
#	vec4 = np.divide(vec4,np.linalg.norm(vec4))
	vec1 = vec1 / np.linalg.norm(vec1)
	vec2 = vec2 / np.linalg.norm(vec2)
	vec3 = vec3 / np.linalg.norm(vec3)
	
#	print('vec1',vec1,'vec3',vec3,'vec4',vec4)
	
	M1[:,0] = vec1
	M1[:,1] = vec2
	M1[:,2] = vec3

#	np.transpose(M1)
#	M1[0,:] = vec1
#	M1[1,:] = vec3
#	M1[2,:] = vec4
	
#	print('det(M)',np.linalg.det(M1))
	
	#inverse kinematics to get euler Z-X-Y order
#	beta = -1*math.asin(M1[2,1])
#	alpha = math.atan2(-1*M1[0,1]/(math.cos(beta)),M1[1,1])/(math.cos(beta))
#	gamma = math.atan2(-1*M1[2,0]/(math.cos(beta)),M1[2,2]/(math.cos(beta)))
#	print('alpha',alpha*180/math.pi,'beta',beta*180/math.pi,'gamma',gamma*180/math.pi)
#	print M1
#	alphastack.append(alpha)
#	alphastack.pop(0)
#	betastack.append(beta)
#	betastack.pop(0)
#	gammastack.append(gamma)
#	gammastack.pop(0)
#	
#	alphafinans = np.mean(alphastack)
#	betafinans = np.mean(betastack)
#	gammafinans = np.mean(gammastack)
	
#	viz.MainView.setEuler(-1*alphafinans*180/math.pi,-1*betafinans*180/math.pi,-1*gammafinans*180/math.pi)
	
#	chksum = 1+M1[0,0]+M1[1,1]+M1[2,2]
#	if (chksum < 0):
#		chksum = 0
#	elif(chksum < -0.5):
#		print('warning poorly condition quaternions!')

	#format quat = (w,x,y,z)
	w = np.math.sqrt(float(1)+M1[0,0]+M1[1,1]+M1[2,2])*0.5
#	print w
	x = (M1[2,1]-M1[1,2])/(4*w)
	y = (M1[0,2]-M1[2,0])/(4*w)
	z = (M1[1,0]-M1[0,1])/(4*w)
	
	alphastack.append(x)
	alphastack.pop(0)
	betastack.append(y)
	betastack.pop(0)
	gammastack.append(z)
	gammastack.pop(0)
	deltastack.append(w)
	deltastack.pop(0)
	
#	yaw = math.atan2(2*(w*x+y*z),1-2*(x*x+y*y))
#	pitch = math.asin(2*(w*y-z*x))
#	roll = math.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
	

#	viz.MainView.setEuler(yaw,pitch,roll)
#	viz.MainView.setQuat(x,-1*z,y,w)
	viz.MainView.setQuat(np.mean(alphastack),-1*np.mean(gammastack),np.mean(betastack),np.mean(deltastack))
	
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
	
root = ''#empty string
savestring = ''
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,))
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
print("\n")

vizact.onkeydown('q',raisestop,'t')
