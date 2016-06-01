#Stepspeed rev4 is the first revision to use the CPP server instead of TMM to get data from Nexus
#wda 1/21/2015

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

def UpdateViz(root,q):
	timeold = time.time()
	
	while not endflag.isSet():
		global histzR
		global histzL
		global rstancetime
		global lstancetime

		root = q.get()#look for the next frame data in the thread queue
		timediff = time.time()-timeold

		lp1 = root.find(".//Forceplate_0/Subframe_0/F_z")#Left Treadmill
		rp1 = root.find(".//Forceplate_1/Subframe_0/F_z")#Right Treadmill

		temp = rp1.attrib.values()
		temp2 = float(temp[0])#cast forceplate data as float
		temp3 = lp1.attrib.values()
		temp4 = float(temp3[0])
		cursorR.setScale(0.1,1.75*lstancetime,0.01250)
		cursorL.setScale(-0.1,1.75*rstancetime,0.01250)
		#check for gait events
		if (temp2 <= -30) & (histzR > -30):#Right HS condition
			rstancetime = rstancetime+timediff
		elif (temp2<-30):
			rstancetime = rstancetime+timediff
		elif (temp2 >-30) & (histzR <= -30):
			HistBallL.setPosition([-0.2,1.75*rstancetime, 0])
			rstancetime = 0
			
		if (temp4 <= -30) & (histzL > -30):#Right HS condition
			lsancetime = lstancetime+timediff
		elif (temp4<-30):
			lstancetime = lstancetime+timediff
		elif (temp4 > -30) & (histzL <= -30):
			HistBallR.setPosition([0.2, 1.75*lstancetime, 0])
			lstancetime = 0
		
		timeold = time.time()
		histzR = temp2
		histzL = temp4
		#update vizard variables!
	
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
t1.daemon = True
t2.daemon = True
#start the threads
t1.start()
t2.start()
print("\n")
print("press 'q' to stop")
print("\n")

vizact.onkeydown('q',raisestop,'t')