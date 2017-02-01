<<<<<<< HEAD
﻿#Stepspeed rev5 shows contralateral stance time for the awareness group in Dulce's study. This revision saves data to verify everything can be reconstructed from the c3d files
#wda 11/3/2015

#rev 5 saves data
#V2P R1

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
import json
import struct


viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)



#setup the VR space with objects
global targetL
targetL = 0.5

global targetR
targetR = 0.5

global targettol
targettol = 0.05
'''
global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol*0.5,0.0125])
boxL.setPosition([-0.2,(targetL-targettol),0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol*0.5,0.0125])
boxR.setPosition([0.2,(targetR-targettol),0])
'''

# Add a purple ball to our world, whose position will later be updated by the data we receive.
global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])

global HistBallR
#HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.04,0.04,0.1], cache=viz.CACHE_NONE)
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.1,0.025,0.0125], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
#HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)
#HistBallR.visible(0)

global HistBallL
#HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.04,0.04,0.1], cache=viz.CACHE_NONE)
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.1,0.025,0.0125], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallR.setEuler(180,0,0)
HistBallL.alpha(0.8)
#HistBallL.visible(0)

viz.MainView.setPosition(0, 0.55, -2)
viz.MainView.setEuler(0,0,0)

global histzR
global histzL
histzR = 0
histzL = 0

global rstancetime
global lstancetime
rstancetime = 0
lstancetime = 0

global RHS
global RTO
global LHS
global LTO

RHS = 0
RTO = 0
LHS = 0
LTO = 0

def UpdateViz(root,q):
	timeold = time.time()
	
	while not endflag.isSet():
		global histzR
		global histzL
		global rstancetime
		global lstancetime
		global RHS
		global RTO
		global LHS
		global LTO
		
		root = q.get()#look for the next frame data in the thread queue
		timediff = time.time()-timeold
		
		lp1 = root.find(".//Forceplate_0/Subframe_0/F_z")#Left Treadmill
		rp1 = root.find(".//Forceplate_1/Subframe_0/F_z")#Right Treadmill
		fn = root.find(".//FrameNumber")#Left Treadmill
		FN = float(fn.attrib.values()[0])

		temp = rp1.attrib.values()
		Rz = float(temp[0])#cast forceplate data as float
		temp3 = lp1.attrib.values()
		Lz = float(temp3[0])
		cursorR.setScale(0.1,lstancetime,0.01250)#display on contralateral side!
		cursorL.setScale(-0.1,rstancetime,0.01250)
		
		#check for gait events
		if (Rz <= -30) & (histzR >-30):#Right HS condition
			rstancetime = rstancetime+timediff
			RHS = 1
			RTO = 0
		elif (Rz<-30):#R stance phase
			rstancetime = rstancetime+timediff
			RHS = 0
			RTO = 0
		elif (Rz >-30) & (histzR <= -30):#RTO
			HistBallL.setPosition([-0.2, rstancetime, 0])#display rstance time on contralateral side
			rstancetime = 0
			RHS = 0
			RTO = 1
			
		if (Lz <= -30) & (histzL >-30):#Left HS condition
			lstancetime = lstancetime+timediff
			LHS = 1
			LTO = 0
		elif (Lz<-30):#Left stance
			lstancetime = lstancetime+timediff
			LHS = 0
			LTO = 0
		elif (Lz > -30) & (histzL <= -30):#LTO 
			HistBallR.setPosition([0.2, lstancetime, 0])#display rstance time on contralateral side
			lstancetime = 0
			LHS = 0
			LTO = 1
		
		timeold = time.time()
		histzR = Rz
		histzL = Lz
		
		savestring = [FN,Rz,Lz,RHS,LHS,RTO,LTO,rstancetime,lstancetime]#organize the data to be written to file
		q3.put(savestring)
		
	print("data stream has completed...")

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
#	q.join()

def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'StepspeedRev5.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RTO','LTO','Rstancetime','Lstancetime'],file)
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
	
endflag = threading.Event()
def raisestop(sign):
	print("stop flag raised")
	endflag.set()
	t1.join()
	t2.join()
	viz.quit()
	
root = ''#empty string
savestring = ''
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q))
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
print("\n")

=======
﻿#Stepspeed rev5 shows contralateral stance time for the awareness group in Dulce's study. This revision saves data to verify everything can be reconstructed from the c3d files
#wda 11/3/2015

#rev 5 saves data
#V2P R1

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
import json
import struct


viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)



#setup the VR space with objects
global targetL
targetL = 0.5

global targetR
targetR = 0.5

global targettol
targettol = 0.05
'''
global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol*0.5,0.0125])
boxL.setPosition([-0.2,(targetL-targettol),0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol*0.5,0.0125])
boxR.setPosition([0.2,(targetR-targettol),0])
'''

# Add a purple ball to our world, whose position will later be updated by the data we receive.
global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])

global HistBallR
#HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.04,0.04,0.1], cache=viz.CACHE_NONE)
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.1,0.025,0.0125], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
#HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)
#HistBallR.visible(0)

global HistBallL
#HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.04,0.04,0.1], cache=viz.CACHE_NONE)
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.1,0.025,0.0125], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallR.setEuler(180,0,0)
HistBallL.alpha(0.8)
#HistBallL.visible(0)

viz.MainView.setPosition(0, 0.55, -2)
viz.MainView.setEuler(0,0,0)

global histzR
global histzL
histzR = 0
histzL = 0

global rstancetime
global lstancetime
rstancetime = 0
lstancetime = 0

global RHS
global RTO
global LHS
global LTO

RHS = 0
RTO = 0
LHS = 0
LTO = 0

def UpdateViz(root,q):
	timeold = time.time()
	
	while not endflag.isSet():
		global histzR
		global histzL
		global rstancetime
		global lstancetime
		global RHS
		global RTO
		global LHS
		global LTO
		
		root = q.get()#look for the next frame data in the thread queue
		timediff = time.time()-timeold
		
		lp1 = root.find(".//Forceplate_0/Subframe_0/F_z")#Left Treadmill
		rp1 = root.find(".//Forceplate_1/Subframe_0/F_z")#Right Treadmill
		fn = root.find(".//FrameNumber")#Left Treadmill
		FN = float(fn.attrib.values()[0])

		temp = rp1.attrib.values()
		Rz = float(temp[0])#cast forceplate data as float
		temp3 = lp1.attrib.values()
		Lz = float(temp3[0])
		cursorR.setScale(0.1,lstancetime,0.01250)#display on contralateral side!
		cursorL.setScale(-0.1,rstancetime,0.01250)
		
		#check for gait events
		if (Rz <= -30) & (histzR >-30):#Right HS condition
			rstancetime = rstancetime+timediff
			RHS = 1
			RTO = 0
		elif (Rz<-30):#R stance phase
			rstancetime = rstancetime+timediff
			RHS = 0
			RTO = 0
		elif (Rz >-30) & (histzR <= -30):#RTO
			HistBallL.setPosition([-0.2, rstancetime, 0])#display rstance time on contralateral side
			rstancetime = 0
			RHS = 0
			RTO = 1
			
		if (Lz <= -30) & (histzL >-30):#Left HS condition
			lstancetime = lstancetime+timediff
			LHS = 1
			LTO = 0
		elif (Lz<-30):#Left stance
			lstancetime = lstancetime+timediff
			LHS = 0
			LTO = 0
		elif (Lz > -30) & (histzL <= -30):#LTO 
			HistBallR.setPosition([0.2, lstancetime, 0])#display rstance time on contralateral side
			lstancetime = 0
			LHS = 0
			LTO = 1
		
		timeold = time.time()
		histzR = Rz
		histzL = Lz
		
		savestring = [FN,Rz,Lz,RHS,LHS,RTO,LTO,rstancetime,lstancetime]#organize the data to be written to file
		q3.put(savestring)
		
	print("data stream has completed...")

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
#	q.join()

def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'StepspeedRev5.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RTO','LTO','Rstancetime','Lstancetime'],file)
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
	
endflag = threading.Event()
def raisestop(sign):
	print("stop flag raised")
	endflag.set()
	t1.join()
	t2.join()
	viz.quit()
	
root = ''#empty string
savestring = ''
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q))
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
print("\n")

>>>>>>> origin/master
vizact.onkeydown('q',raisestop,'t')