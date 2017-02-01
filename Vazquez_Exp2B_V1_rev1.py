<<<<<<< HEAD
﻿#Exp2B V1 from "Perceptual Sensory Correlates of Split Belt Walking Adaptation"
#Replicate of experiment 2B from this paper
#
#Subjects walk at a set speed, for 30 seconds they try to match anterior hip-ankle distance at HS with the left or "slow" leg HS. 
#targets are displayed on a latitudinal grid, 20 targets, 2 cm apart. The left leg target appears as a red circle.
#
#V1 is the true evaluative form of 2B, V2 is a training version where subjects see the right leg feedback.
#
#V2P_DK2_R1
#
#William Anderton 1/12/2015

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
#import xml.etree.cElementTree as ElementTree
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

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN #run world in full screen
)
time.sleep(1)#show off our cool logo, not really required but cool


#global messagewin
#messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)

#global targetCENTER
#targetCENTER = 0.21

global targetSLOW
targetSLOW = 0.2

global targettol
targettol = 0.02

global circleL #slow leg circle marker
circleL = vizshape.addSphere(0.01,20,20,color=viz.RED)
circleL.setPosition(-0.1,targetSLOW,0)
circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

#create latitudinal grid
lines = {}#create empty dictionary
for x in range(1,23,1):
	lines["T{0}".format(x)]=vizshape.addBox(size=[1,0.001,0.001])
	lines["T{0}".format(x)].setPosition(0,(x-1)*0.02,0)
#	print((x-1)*0.02)
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	


viz.MainView.setPosition(0, 0.21, -0.57)
viz.MainView.setEuler(0,0,0)

global histzR
histzR = 0
global histzL
histzL = 0

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


def updatetargetdisplay(ts,vizobj,flag):  #distance value, circle object, flag=1 for left, anything else for right
	global tnums
#	print(tnums)
	#figure out which target to place circle in and highlight the number
	ts = abs(ts)*100 #convert units to centimeters for rounding
	print("ts",ts)
	oddnum = np.floor(ts / 2.) * 2 + 1 #round to the nearest odd integer
#	print("oddnum",int(oddnum))
	index = int((oddnum-1)/2)
#	print("index",index)
	#turn the other target numbers back to white
	for i in [x for x in xrange(21) if x != int(index)]:
		tnums["Num{0}".format(i)].color(viz.WHITE)
	#highlight the selected target
	tnums["Num{0}".format(int(index))].color(viz.RED)
	
	#update position of circle
#	vizobj.setPosition(-0.1,oddnum/100,0)
	if (flag == 1):
#		vizobj.setPosition(-0.1,ts/100,0) #analog placement
		vizobj.setPosition(-0.1,oddnum/100,0)#discrete placement
	else:
#		vizobj.setPosition(0.1,ts/100,0) #analog placement
#		vizobj.setPosition(0.05,oddnum/100,0) #discrete placement
		pass
		
	return index #return in units of meters
	
global targetnum
targetnum = updatetargetdisplay(targetSLOW,circleL,1)
	

def UpdateViz(root,q,speedlist,qq,savestring,q3):

	global histzL
	global histzR
	global targetSLOW
	global circleL
	global rgorb
	global lgorb
	global cpps
	global Rerror
	global Lerror
	global targetnum
	global targettol
	global RHS
	global LHS
	
	
	while not endflag.isSet():
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		#look for marker data
		try:
			RANKY = float(data["RANK"][1])/1000
			LANKY = float(data["LANK"][1])/1000
			RHIPY = float(data["RGT"][1])/1000
			LHIPY = float(data["LGT"][1])/1000
			
		except:
			try:
				RHIPY = float(data["RHIP"][1])/1000
				LHIPY = float(data["LHIP"][1])/1000
			except:
				print(["ERROR: incorrect or missing marker data..."])
		
#		print("RANKY",RANKY)

		Ralpha = (RHIPY+LHIPY)/2-RANKY
		Lalpha = (LHIPY+RHIPY)/2-LANKY
		
		#gait events
		if (Rz <= -30) & (histzR > -30):#RHS
			Rerror = targetSLOW-Ralpha
			if (Rerror < targettol):
				rgorb = 1
			else:
				rgorb = 0
			
		if (Lz <= -30) & (histzL > -30):#LHS
			Lerror = targetSLOW-Lalpha
			if (Lerror < targettol):
				lgorb = 1
			else:
				lgorb = 0
			targetnum = updatetargetdisplay(Lalpha,circleL,1)
			targetSLOW = Lalpha

		
		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,Ralpha,Lalpha,Rerror,Lerror,targetnum,]#organize the data to be written to file
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
	mststring = str(mst2)+'EXP2B_V1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RGORB','LGORB','Ralpha','Lalpha','Rerror','Lerror','targetnumber'],file)
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
#	t1.join(5)
#	t2.join(5)
#	t3.join(5)
#	t4.join(5)
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
#t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
#t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
#t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	














=======
﻿#Exp2B V1 from "Perceptual Sensory Correlates of Split Belt Walking Adaptation"
#Replicate of experiment 2B from this paper
#
#Subjects walk at a set speed, for 30 seconds they try to match anterior hip-ankle distance at HS with the left or "slow" leg HS. 
#targets are displayed on a latitudinal grid, 20 targets, 2 cm apart. The left leg target appears as a red circle.
#
#V1 is the true evaluative form of 2B, V2 is a training version where subjects see the right leg feedback.
#
#V2P_DK2_R1
#
#William Anderton 1/12/2015

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
#import xml.etree.cElementTree as ElementTree
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

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN #run world in full screen
)
time.sleep(1)#show off our cool logo, not really required but cool


#global messagewin
#messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)

#global targetCENTER
#targetCENTER = 0.21

global targetSLOW
targetSLOW = 0.2

global targettol
targettol = 0.02

global circleL #slow leg circle marker
circleL = vizshape.addSphere(0.01,20,20,color=viz.RED)
circleL.setPosition(-0.1,targetSLOW,0)
circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

#create latitudinal grid
lines = {}#create empty dictionary
for x in range(1,23,1):
	lines["T{0}".format(x)]=vizshape.addBox(size=[1,0.001,0.001])
	lines["T{0}".format(x)].setPosition(0,(x-1)*0.02,0)
#	print((x-1)*0.02)
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	


viz.MainView.setPosition(0, 0.21, -0.57)
viz.MainView.setEuler(0,0,0)

global histzR
histzR = 0
global histzL
histzL = 0

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


def updatetargetdisplay(ts,vizobj,flag):  #distance value, circle object, flag=1 for left, anything else for right
	global tnums
#	print(tnums)
	#figure out which target to place circle in and highlight the number
	ts = abs(ts)*100 #convert units to centimeters for rounding
	print("ts",ts)
	oddnum = np.floor(ts / 2.) * 2 + 1 #round to the nearest odd integer
#	print("oddnum",int(oddnum))
	index = int((oddnum-1)/2)
#	print("index",index)
	#turn the other target numbers back to white
	for i in [x for x in xrange(21) if x != int(index)]:
		tnums["Num{0}".format(i)].color(viz.WHITE)
	#highlight the selected target
	tnums["Num{0}".format(int(index))].color(viz.RED)
	
	#update position of circle
#	vizobj.setPosition(-0.1,oddnum/100,0)
	if (flag == 1):
#		vizobj.setPosition(-0.1,ts/100,0) #analog placement
		vizobj.setPosition(-0.1,oddnum/100,0)#discrete placement
	else:
#		vizobj.setPosition(0.1,ts/100,0) #analog placement
#		vizobj.setPosition(0.05,oddnum/100,0) #discrete placement
		pass
		
	return index #return in units of meters
	
global targetnum
targetnum = updatetargetdisplay(targetSLOW,circleL,1)
	

def UpdateViz(root,q,speedlist,qq,savestring,q3):

	global histzL
	global histzR
	global targetSLOW
	global circleL
	global rgorb
	global lgorb
	global cpps
	global Rerror
	global Lerror
	global targetnum
	global targettol
	global RHS
	global LHS
	
	
	while not endflag.isSet():
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		#look for marker data
		try:
			RANKY = float(data["RANK"][1])/1000
			LANKY = float(data["LANK"][1])/1000
			RHIPY = float(data["RGT"][1])/1000
			LHIPY = float(data["LGT"][1])/1000
			
		except:
			try:
				RHIPY = float(data["RHIP"][1])/1000
				LHIPY = float(data["LHIP"][1])/1000
			except:
				print(["ERROR: incorrect or missing marker data..."])
		
#		print("RANKY",RANKY)

		Ralpha = (RHIPY+LHIPY)/2-RANKY
		Lalpha = (LHIPY+RHIPY)/2-LANKY
		
		#gait events
		if (Rz <= -30) & (histzR > -30):#RHS
			Rerror = targetSLOW-Ralpha
			if (Rerror < targettol):
				rgorb = 1
			else:
				rgorb = 0
			
		if (Lz <= -30) & (histzL > -30):#LHS
			Lerror = targetSLOW-Lalpha
			if (Lerror < targettol):
				lgorb = 1
			else:
				lgorb = 0
			targetnum = updatetargetdisplay(Lalpha,circleL,1)
			targetSLOW = Lalpha

		
		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,Ralpha,Lalpha,Rerror,Lerror,targetnum,]#organize the data to be written to file
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
	mststring = str(mst2)+'EXP2B_V1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RGORB','LGORB','Ralpha','Lalpha','Rerror','Lerror','targetnumber'],file)
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
#	t1.join(5)
#	t2.join(5)
#	t3.join(5)
#	t4.join(5)
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
#t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
#t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
#t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	














>>>>>>> origin/master
