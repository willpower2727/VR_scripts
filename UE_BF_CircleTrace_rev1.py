<<<<<<< HEAD
﻿#Upper Extremity Cirlce trace BF task
#rev 1 8/10/2015
#William Anderton
#Uses V2P R1 

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
import vizshape
import math

#check vizard4/bin/vizconfig to change which monitor displays the VR window
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)

#viz.startLayer(viz.LINES) 
#viz.vertex(-0.185,0,1) #Vertices are split into pairs. 
#viz.vertex(0.185,0,1) 
#myLines = viz.endLayer() 

global Tdiam
Tdiam = 0.185
global Tol
Tol = 0.005
global target
target = vizshape.addTorus((Tdiam-Tol)/2,2*Tol,40,axis=vizshape.AXIS_Y)
target.setEuler(0,90,0)
target.setPosition(0,0,1)
target.color([0.5,0.5,0.5])
target.disable(viz.LIGHTING)


global cursor
cursor = vizshape.addSphere(radius=0.005,slices=20,stacks=20,axis=vizshape.AXIS_Y)
cursor.setPosition(0,0,0.98)
cursor.color(viz.YELLOW)
cursor.disable(viz.LIGHTING)

global Xoff
global Yoff
Xoff = 0
Yoff = 0

global xold
global yold
xold = 0
yold = 0

global tracer
viz.startLayer(viz.LINES)
viz.vertexColor(viz.YELLOW)
tracer = viz.endLayer(viz.WORLD,viz.MainScene)
tracer.dynamic()

global tcounter
tcounter = 0

global trialflag
trialflag = 0

viz.MainView.setPosition(0, 0,0)
viz.MainView.setEuler(0,0,0)


def UpdateViz(root,q,savestring,q3):
	

	while not endflag.isSet():
		global target
		global cursor
		global Xoff
		global Yoff
		global xold
		global yold
		global tracer
		global tcounter
		global trialflag
		global Tdiam

		root = q.get()#look for the next frame data in the thread queue

#		lp1 = root.find(".//FP_0/SubF_8/Fz")#Left Treadmill
#		rp1 = root.find(".//FP_1/SubF_8/Fz")#Right Treadmill
		tipx = root.find(".//Subject0/TIP/X")
		tipy = root.find(".//Subject0/TIP/Y")
		
		try:
			temp = tipx.attrib.values()
			X = -1*float(temp[0])#cast forceplate data as float
			temp3 = tipy.attrib.values()
			Y = -1*float(temp3[0])
		except:
			print 'No marker data available'
			X = 0
			Y = 0
		
#		print(X/1000-Xoff,Y/1000-Yoff)
		cursor.setPosition(X/1000-Xoff,Y/1000-Yoff,0.98)
		
		#add trace
#		if trialinprog.is_set():
#			if (X-xold < 0.002) | (Y-yold < 0.002):
	#			print(X-xold)
#				pass
#			elif (tcounter > 3):
#				tracer.addVertex(X/1000-Xoff,Y/1000-Yoff,0.98)
#				tcounter = 0
#			else:
#				tracer.addVertex(X/1000-Xoff,Y/1000-Yoff,0.98)
#				tcounter = tcounter+1
	#			print 'vertex added'
	
		#compute the radius of x,y coord and see if it's within tolerance
		R = math.sqrt((X/1000-Xoff)**2+(Y/1000-Yoff)**2)
#		print R
		
		if (abs(R-Tdiam/2)<Tol):# | ((Tdiam/2-R)<Tol):
			target.color([0.4,0.7,0])
		else:
			target.color([0.5,0.5,0.5])
			
		fn = root.find(".//FrameNumber")#Left Treadmill
		fnn = fn.attrib.values()
		savestring = [int(fnn[0]),X,Y,trialflag]
#		print(sys.getsizeof(savestring))
		q3.put(savestring)
#		print(q3.qsize())
		xold = X
		yold = Y
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
	mststring = str(mst2)+'UE_circletrace.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','X','Y','flag'],file)
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

trialinprog = threading.Event()
def startset(q):
	global Xoff
	global Yoff
	global tracer
	global Tdiam
	global target
	global trialflag
	
	trialflag = 1
	
	target.setScale(1,1,1)
	tracer.clearVertices()
	trialinprog.set()
	root = q.get()
	tipx = root.find(".//Subject0/TIP/X")
	tipy = root.find(".//Subject0/TIP/Y")
	try:
		temp = tipx.attrib.values()
		Xoff = -1*float(temp[0])/1000#cast forceplate data as float
		temp3 = tipy.attrib.values()
		Yoff = -1*float(temp3[0])/1000+Tdiam/2
	except:
		print 'No marker data available'
		Xoff = 0
		Yoff = 0
		
def perturb(q):
	global target
	target.setScale(1.2,1,1)
	
def stopset(q):
	global trialflag
	global target
	global tracer
	tracer.clearVertices()
	target.setScale(1,1,1)
	trialflag = 0
	


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
vizact.onkeydown('b',startset,q)
vizact.onkeydown('n',perturb,q)
=======
﻿#Upper Extremity Cirlce trace BF task
#rev 1 8/10/2015
#William Anderton
#Uses V2P R1 

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
import vizshape
import math

#check vizard4/bin/vizconfig to change which monitor displays the VR window
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)

#viz.startLayer(viz.LINES) 
#viz.vertex(-0.185,0,1) #Vertices are split into pairs. 
#viz.vertex(0.185,0,1) 
#myLines = viz.endLayer() 

global Tdiam
Tdiam = 0.185
global Tol
Tol = 0.005
global target
target = vizshape.addTorus((Tdiam-Tol)/2,2*Tol,40,axis=vizshape.AXIS_Y)
target.setEuler(0,90,0)
target.setPosition(0,0,1)
target.color([0.5,0.5,0.5])
target.disable(viz.LIGHTING)


global cursor
cursor = vizshape.addSphere(radius=0.005,slices=20,stacks=20,axis=vizshape.AXIS_Y)
cursor.setPosition(0,0,0.98)
cursor.color(viz.YELLOW)
cursor.disable(viz.LIGHTING)

global Xoff
global Yoff
Xoff = 0
Yoff = 0

global xold
global yold
xold = 0
yold = 0

global tracer
viz.startLayer(viz.LINES)
viz.vertexColor(viz.YELLOW)
tracer = viz.endLayer(viz.WORLD,viz.MainScene)
tracer.dynamic()

global tcounter
tcounter = 0

global trialflag
trialflag = 0

viz.MainView.setPosition(0, 0,0)
viz.MainView.setEuler(0,0,0)


def UpdateViz(root,q,savestring,q3):
	

	while not endflag.isSet():
		global target
		global cursor
		global Xoff
		global Yoff
		global xold
		global yold
		global tracer
		global tcounter
		global trialflag
		global Tdiam

		root = q.get()#look for the next frame data in the thread queue

#		lp1 = root.find(".//FP_0/SubF_8/Fz")#Left Treadmill
#		rp1 = root.find(".//FP_1/SubF_8/Fz")#Right Treadmill
		tipx = root.find(".//Subject0/TIP/X")
		tipy = root.find(".//Subject0/TIP/Y")
		
		try:
			temp = tipx.attrib.values()
			X = -1*float(temp[0])#cast forceplate data as float
			temp3 = tipy.attrib.values()
			Y = -1*float(temp3[0])
		except:
			print 'No marker data available'
			X = 0
			Y = 0
		
#		print(X/1000-Xoff,Y/1000-Yoff)
		cursor.setPosition(X/1000-Xoff,Y/1000-Yoff,0.98)
		
		#add trace
#		if trialinprog.is_set():
#			if (X-xold < 0.002) | (Y-yold < 0.002):
	#			print(X-xold)
#				pass
#			elif (tcounter > 3):
#				tracer.addVertex(X/1000-Xoff,Y/1000-Yoff,0.98)
#				tcounter = 0
#			else:
#				tracer.addVertex(X/1000-Xoff,Y/1000-Yoff,0.98)
#				tcounter = tcounter+1
	#			print 'vertex added'
	
		#compute the radius of x,y coord and see if it's within tolerance
		R = math.sqrt((X/1000-Xoff)**2+(Y/1000-Yoff)**2)
#		print R
		
		if (abs(R-Tdiam/2)<Tol):# | ((Tdiam/2-R)<Tol):
			target.color([0.4,0.7,0])
		else:
			target.color([0.5,0.5,0.5])
			
		fn = root.find(".//FrameNumber")#Left Treadmill
		fnn = fn.attrib.values()
		savestring = [int(fnn[0]),X,Y,trialflag]
#		print(sys.getsizeof(savestring))
		q3.put(savestring)
#		print(q3.qsize())
		xold = X
		yold = Y
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
	mststring = str(mst2)+'UE_circletrace.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','X','Y','flag'],file)
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

trialinprog = threading.Event()
def startset(q):
	global Xoff
	global Yoff
	global tracer
	global Tdiam
	global target
	global trialflag
	
	trialflag = 1
	
	target.setScale(1,1,1)
	tracer.clearVertices()
	trialinprog.set()
	root = q.get()
	tipx = root.find(".//Subject0/TIP/X")
	tipy = root.find(".//Subject0/TIP/Y")
	try:
		temp = tipx.attrib.values()
		Xoff = -1*float(temp[0])/1000#cast forceplate data as float
		temp3 = tipy.attrib.values()
		Yoff = -1*float(temp3[0])/1000+Tdiam/2
	except:
		print 'No marker data available'
		Xoff = 0
		Yoff = 0
		
def perturb(q):
	global target
	target.setScale(1.2,1,1)
	
def stopset(q):
	global trialflag
	global target
	global tracer
	tracer.clearVertices()
	target.setScale(1,1,1)
	trialflag = 0
	


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
vizact.onkeydown('b',startset,q)
vizact.onkeydown('n',perturb,q)
>>>>>>> origin/master
vizact.onkeydown('m',stopset,q)