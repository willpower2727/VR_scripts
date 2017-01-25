#This script displays real time biofeedback on Step Length Assymetry 
#target heights are time invariant values determined from baseline walking
#i.e. try to walk with perfect symmetry, or walk with 0.2 assymetry

#WDA 10/9/2015
#
#Requirements:
#
#Nexus 1.x or 2.x
#system config: MAR_BF_DEFAULT
#
#assumes the left treadmill is called "Left" and the right is called "Right"
#
#Tested 10/12/2015  120 Hz server push mode
#
#Use V2P_DK2_R1

import viz
import time
import socket
import sys
import io
import re
import threading
import Queue
import json
import vizact
import vizinfo
import random
import itertools
import struct
import array
import math
import scipy
import numpy as np
import oculus
import vizmat
import vizlens

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN #run world in full screen
)
time.sleep(2)#show off our cool logo, not really required but cool

global scaler #for asthetic purposes
scaler = 3

#set target tolerance for stride length
global targetL
targetL = 0.1

global targetR
targetR = 0.1

global targettol
targettol = 0.005

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxL.setPosition([-0.2,targetL*scaler,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxR.setPosition([0.2,targetR*scaler,0])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])

viz.MainView.setPosition(0, 0.25, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels
#global RCOUNT
#global LCOUNT
#RCOUNT = 0
#LCOUNT = 0
##rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
#rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR-0.2,12])
##leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
#leftcounter = viz.addText(str(LCOUNT),pos=[-4.4,targetL-0.2,12])

global Rforceold
global Lforceold
Rforceold = -50
Lforceold = -50

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

global fast
fast = 0
global slow
slow = 0

global RHS
RHS = 0
global LHS
LHs = 0


def UpdateViz(root,q,speedlist,qq,savestring,q3):

	while not endflag.isSet():
		global cursorR
		global cursorL
		global HistBallR
		global HistBallL
		global boxL
		global boxR
		global targettol
		global targetR
		global targetL
		global steplengthL
		global steplengthR
		global Rforceold
		global Lforceold
		global fast
		global slow
		global RHS
		global LHS
		
		root = q.get()
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
#		RHIPY = float(data["RHIP"][1])/1000
#		LHIPY = float(data["LHIP"][1])/1000
		RHIPY = float(data["RGT"][1])/1000
		LHIPY = float(data["LGT"][1])/1000
		RANKY = float(data["RANK"][1])/1000
		LANKY = float(data["LANK"][1])/1000
		
		#definition step length assymetry
		#(fast-slow)/(fast+slow)
		#
		#fast is ankle-ankle distance at fast HS, slow is at slow HS
		
		fast = (LANKY-RANKY)/(LANKY+RANKY) # step length assymetry
		slow = (RANKY-LANKY)/(LANKY+RANKY)
		
		cursorR.setScale(0.1,fast,0.0125)
		cursorL.setScale(0.1,slow,0.0125)
		
		if (fast > 0) & (Rz > -10):#swing phase of fast leg
			cursorR.visible(1)
		else:
			cursorR.visible(0)
			
		if (slow > 0) & (Lz > -10):
			cursorL.visible(1)
		else:
			cursorL.visible(0)
			
		
		#RHS
		if (Rforceold >= -30) & (Rz < -30):
			HistBallR.setPosition([0.2,fast,0])
			steplengthR = fast
			RHS = 1
		else:
			RHS = 0
		#LHS
		if (Lforceold >= -30) & (Lz < -30):
			HistBallL.setPosition([-0.2,slow,0])
			steplengthL = slow
			LHS = 1
		else:
			LHS = 0
		
		Rforceold = Rz
		Lforceold = Lz
		
		savestring = [FN,Rz,Lz,RHIPY,LHIPY,RANKY,LANKY,fast,slow,RHS,LHS]
		q3.put(savestring)
		
		#calculate step lengths

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
	mststring = str(mst2)+'EffortStudy_R1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHIPy','LHIPy','RANky','LANKy','fastSLASYM','slowSLASYM'],file)
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
	
def ParseRoot(root):#the purpose of this function is to make sure that marker data is used correctly since they can arrive in different order, depending on the order the models are listed in Nexus
	tempdat = root.split(',')
#	print tempdat
	del tempdat[-1]#the last element is a empty string ""
	data = {}#create dictionary
	
	data["FN"] = int(tempdat[0])#frame number
	data["Rz"] = float(tempdat[4])#right forceplate Z component
	data["Lz"] = float(tempdat[2])#left forceplate Z comp.
	data["SYNC"] = float(tempdat[6])#sync data
	
	#check to see if there is more analog data
	
	#place marker data into dictionary
	for z in range(7,len(tempdat),4):
		temp = tempdat[z]
#		print temp
		data[temp] = [tempdat[z+1],tempdat[z+2],tempdat[z+3]]
		
#	print data
	return data
	
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
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq,savestring,q3))
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
	