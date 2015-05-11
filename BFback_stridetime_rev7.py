#Stridetime rev7 is the first revision to use the CPP server instead of TMM to get data from Nexus
#wda 1/21/2015
#modified 3/17/2015 to test Vicon2Python_rev2, faster

import socket
import sys
import io
import re
import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import json
import vizact

#check vizard4/bin/vizconfig to change which monitor displays the VR window
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)

#setup the VR space with objects
global scalorxx
scalorxx = 0.6667
global targetL
targetL = 1
global targetR
targetR = 1
global targettol
targettol = 0.05
global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.04)*0.75,0.0125])
boxL.setPosition([-0.2,targetL*scalorxx,0])
global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.04)*0.75,0.0125])
boxR.setPosition([0.2,targetR*scalorxx,0])
global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])
global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])
global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.03,0.03,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR*scalorxx,0])
HistBallR.setEuler(0,0,0)
HistBallR.alpha(0.8)
global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.03,0.03,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL*scalorxx,0])
HistBallR.setEuler(180,0,0)
HistBallL.alpha(0.8)

viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)

global histzR
global histzL
histzR = 0
histzL = 0

global rstridetime
global lstridetime
rstridetime = 0
lstridetime = 0

#global RHS
#global LHS
#RHS = 0
#LHS = 0
global FNold
FNold = 0


def UpdateViz(root,q,savestring,q3):
	timeold = time.time()
	RHS = 0
	LHS = 0

	while not endflag.isSet():
		global targetR
		global targettol
		global histzR
		global histzL
		global rstridetime
		global lstridetime
#		print(Queue.Queue.qsize(q))
		root = q.get()#look for the next frame data in the thread queue
#		q.task_done()
#		print(Queue.Queue.qsize(q))
		timediff = time.time()-timeold

		lp1 = root.find(".//FP_0/SubF_8/Fz")#Left Treadmill
		rp1 = root.find(".//FP_1/SubF_8/Fz")#Right Treadmill

		temp = rp1.attrib.values()
		Rz = float(temp[0])#cast forceplate data as float
		temp3 = lp1.attrib.values()
		Lz = float(temp3[0])
		cursorR.setScale(0.1,rstridetime*scalorxx,0.01250)
		cursorL.setScale(-0.1,lstridetime*scalorxx,0.01250)
		#check for gait events
		if (Rz < -30) & (histzR >= -30):#HS condition
			HistBallR.setPosition([0.2, rstridetime*scalorxx, 0])
			RHS = 1
			if (abs(rstridetime-targetR) <= targettol):
				boxR.color( viz.WHITE )
			else:
				boxR.color( viz.BLUE )
			rstridetime = 0
		else:
			rstridetime = rstridetime+timediff
			RHS = 0
			
		if (Lz < -30) & (histzL >= -30):
			HistBallL.setPosition([-0.2, lstridetime*scalorxx, 0])
			LHS = 1
			if (abs(lstridetime-targetL) <= targettol):
				boxL.color( viz.WHITE )
			else:
				boxL.color( viz.BLUE )
			lstridetime = 0
		else:
			lstridetime = lstridetime+timediff
			LHS = 0
		
		timeold = time.time()
		histzR = Rz
		histzL = Lz
		
		#send some data to be saved
		fn = root.find(".//FN")#Left Treadmill
		fnn = fn.attrib.values()
#		print(fnn[0])
		
		savestring = [int(fnn[0]),Rz,Lz,RHS,LHS]
#		print(sys.getsizeof(savestring))
		q3.put(savestring)
#		print(q3.qsize())
	q3.join()
	print("data has all been gotten")

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
	mststring = str(mst2)+'StrideTime.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS'],file)
	file.close()
	
	file = open(mststring,'a')#reopen for appending only
	print('file is open for appending')
	while not endflag.isSet():
#		print(q3.empty())
		savestring = q3.get()#look in the queue for data to write
#		print(savestring)
		q3.task_done()
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
	t4.join()
	viz.quit()



root = ''#empty string
savestring = ''
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,savestring,q3))
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

vizact.onkeydown('q',raisestop,'t')
