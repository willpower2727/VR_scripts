""" Biofeedback routine for step time, from HS to HS

This script updates left and right cursors based on step time, using a flip-flop technique

WDA 1/22/2015

rev5 is the first revision to use Python2CPP client as source of data instead of TMM

V2P R1
"""

import socket
import sys
import io
import re
#from xml.etree import ElementTree
import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN
)

#set target tolerance for step time
global targetL
targetL = 0.9

global targetR
targetR = 0.9

global targettol
targettol = 0.05

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxL.setPosition([-0.2,targetL,0.05])#target box needs to be a little offset from pure target altittude since perspective can make biofeedback seem dishonest, good feedback appears when it looks like value is outside target box

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxR.setPosition([0.2,targetR,0.05])

viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR-0.2,12])
leftcounter = viz.addText(str(LCOUNT),pos=[-4.4,targetL-0.2,12])

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
#HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallR.setEuler(180,0,0)
HistBallL.alpha(0.8)

global histzR
histzR = 0
global histzL
histzL = 0
global steptime
steptime = 0

def UpdateViz(root,q):
	global targetL
	global targetR
	global targettol
	global histzR
	global histzL
	global steptime
	timeold = time.time()
	
	while not endflag.isSet():
		root = q.get()
		timediff = time.time()-timeold
		lp1 = root.find(".//Forceplate_0/Subframe_0/F_z")#Left Treadmill
		rp1 = root.find(".//Forceplate_1/Subframe_0/F_z")#Right Treadmill

		temp = rp1.attrib.values()
		Rz = float(temp[0])#cast forceplate data as float
		temp3 = lp1.attrib.values()
		Lz = float(temp3[0])
		
		if (Rz < -30) & (histzR >= -30):#RHS
			cursorR.visible(0)# hide right side show left
			cursorL.visible(1)
			if (abs(steptime - targetR) < targettol):
				boxR.color( viz.WHITE )
			else:
				boxR.color( viz.BLUE )
			HistBallR.setPosition([0.2, steptime, 0])
			steptime = 0
		elif (Lz < -30) & (histzL >= -30): #LHS
			cursorR.visible(1)
			cursorL.visible(0)
			if (abs(steptime - targetL) < targettol):
				boxL.color( viz.WHITE )
			else:
				boxL.color( viz.BLUE )
			HistBallL.setPosition([-0.2, steptime, 0])
			steptime = 0
		else:
			steptime = steptime + timediff
		#change the heights
		cursorR.setScale(0.1,steptime,0.01250)
		cursorL.setScale(-0.1,steptime,0.01250)
		
		timeold = time.time()
		histzR = Rz
		histzL = Lz
		
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
#			path = root.find("FrameNumber")
#			print(path.attrib)
			q.put(root)#place the etree into the threading queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()

endflag = threading.Event()
def raisestop(sign):
	print("stop flag raised")
	endflag.set()
	t1.join()
	t2.join()
	viz.quit()
	
root = ''#empty string
q = Queue.Queue()#initialize the queue
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q))
#start the threads
t1.start()
t2.start()

print("\n")
print("press 'q' to stop")
print("\n")

vizact.onkeydown('q',raisestop,'t')