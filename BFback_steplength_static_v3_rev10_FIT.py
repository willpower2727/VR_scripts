""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 3 feedback, cursor, and target are on.
rev10 is identicle to rev8 except it is using the new python Nexus server app, not TMM
wda 1/27/2015
"""
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
from xml.etree import ElementTree
import threading
import Queue
import time
import struct
import array

viz.go(
#viz.FULLSCREEN #run world in full screen
)

#set target tolerance for stride length
global targetL
targetL = 0.3
global targetR
targetR = 0.3

global targettol
targettol = 0.025# 5cm

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =20
#setup array of randomly picked steps
global randy
randy  = [1] * STEPNUM + [2] * STEPNUM # create list of 1's and 2's 
random.shuffle(randy)#randomize the order of tests
random.shuffle(randy)#randomize the order of tests again
#print(randy)

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxL.setPosition([-0.2,targetL,0.05])

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxR.setPosition([0.2,targetR,.05])

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0

rightcounter = viz.addText(str(RCOUNT),pos=[.4,0,0],scale=[0.1,0.1,0.1])
leftcounter = viz.addText(str(LCOUNT),pos=[-.46,0,0],scale=[0.1,0.1,0.1])

global RGOB
RGOB = 0 #this will be 0 or 1, depending on success or failure
global LGOB
LGOB = 0
global stepind #this keeps track of the total # of attempts
stepind = 0

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,targetR,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,targetL,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)

global histzR
histzR = 0
global histzL
histzL = 0

global steplengthL
steplengthL = 0
global steplengthR
steplengthR = 0

global Rattempts
Rattempts = 0
global Lattempts
Lattempts = 0

global old0
old0 = 0
global old1
old1 = 0

viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)

def UpdateViz(root,q,speedlist,qq):
	timeold = time.time()
	
	while 1:
		global cursorL
		global cursorR
		global HistBallL
		global HistBallR
		global histzL
		global histzR
		global STEPNUM
		global Rattempts
		global Lattempts
		global stepind
		global RCOUNT
		global LCOUNT
		global randy
		
		root = q.get()#look for the next frame data in the thread queue
		if root is None:
			continue
		else:
			timediff = time.time()-timeold
			
			#find the data we need from the frame packet
			lp1 = root.find(".//Forceplate_0/Subframe_0/F_z")#Left Treadmill
			rp1 = root.find(".//Forceplate_1/Subframe_0/F_z")#Right Treadmill
			s0rhipy = root.find(".//Subject0/RHIP/Y")
			s0lhipy = root.find(".//Subject0/LHIP/Y")
			s0ranky = root.find(".//Subject0/RANK/Y")
			s0lanky = root.find(".//Subject0/LANK/Y")

			temp = rp1.attrib.values()
			Rz = float(temp[0])#cast forceplate data as float
			temp1 = lp1.attrib.values()
			Lz = float(temp1[0])
#			temp2 = s0rhipy.attrib.values()
#			RHIPY = float(temp2[0])/1000
#			temp3 = s0lhipy.attrib.values()
#			LHIPY = float(temp3[0])/1000
			temp4 = s0ranky.attrib.values()
			RANKY = float(temp4[0])/1000
			temp5 = s0lanky.attrib.values()
			LANKY = float(temp5[0])/1000
			
#			HIPY = (RHIPY+LHIPY)/2#average hip position in the Y direction
#			print(HIPY-RANKY)
			#start making updates
			cursorR.setScale(0.1,LANKY-RANKY,0.01250)
			cursorL.setScale(-0.1,RANKY-LANKY,0.01250)
			
			if (LANKY-RANKY < 0):
				cursorR.visible(0)
				neutralR.visible(1)
			else:
				cursorR.visible(1)
				neutralR.visible(0)
				
			if (RANKY-LANKY < 0):
				cursorL.visible(0)
				neutralL.visible(1)
			else:
				cursorL.visible(1)
				neutralL.visible(0)
			
			if (Rz < -30) & (histzR >= -30):#RHS condition
				stepind = stepind+1
				Rattempts = Rattempts+1
				
				HistBallR.setPosition([0.2,LANKY-RANKY, 0])
				if (abs((LANKY-RANKY)-targetR) <= targettol):
					RCOUNT = RCOUNT+1
					boxR.color( viz.WHITE )
				else:
					boxR.color( viz.BLUE )
			rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
			
			if (Lz < -30) & (histzL >= -30):#LHS condition
				stepind = stepind+1
				Lattempts = Lattempts+1
				
				HistBallL.setPosition([-0.2,RANKY-LANKY, 0])
				if (abs((RANKY-LANKY)-targetL) <= targettol):
					LCOUNT = LCOUNT+1
					boxL.color( viz.WHITE )
				else:
					boxL.color( viz.BLUE )
			leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
			
			
			if (LANKY-RANKY < targetR/2) & (LANKY-RANKY > targetR/2-0.01) & (Rz < -30):#time to hide the targets before next step
				boxR.color( viz.BLUE )#change colors of targets back to default blue
				boxL.color( viz.BLUE )
				boxR.visible(0)
				boxL.visible(0)
				HistBallR.visible(0)#hide until the next HS
				HistBallL.visible(0)
			if (RANKY-LANKY < targetL/2) & (RANKY-LANKY > targetL/2-0.01) & (Lz < -30):#time to hide the targets before next step
				boxR.color( viz.BLUE )#change colors of targets back to default blue
				boxL.color( viz.BLUE )
				boxR.visible(0)
				boxL.visible(0)
				HistBallR.visible(0)#hide until the next HS
				HistBallL.visible(0)
				
			if (Rz < -50) & (LANKY-RANKY > 0.05):#check to see if the treadmill needs to move the feet back to neutral
				speedlist = [200,0,1000,1000,0]
				qq.put(speedlist)
			elif (Lz < -50) & (RANKY-LANKY > 0.05):
				speedlist = [0,200,1000,1000,0]
				qq.put(speedlist)
			else:
				speedlist = [0,0,1000,1000,0]
				qq.put(speedlist)
				if (randy[stepind]  == 1):#when the feet are back together, display the new target
					boxR.visible(1)
					boxL.visible(0)
				else:
					boxR.visible(0)
					boxL.visible(1)
			
			
			histzR = Rz
			histzL = Lz
			timeold = time.time()

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
	while 1:
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
			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			q.put(root)#place the etree into the threading queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()

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

	while 1:
		
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

	s2.close()
	
	
root = ''#empty string
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq))
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
#start the threads
t1.start()
t2.start()
t3.start()
	

