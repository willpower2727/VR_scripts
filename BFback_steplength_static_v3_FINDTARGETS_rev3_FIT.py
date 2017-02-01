<<<<<<< HEAD
﻿""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing plugin gait with hip marker set.

In version 3 FINDTARGETS rev3, feedback, cursor, on, targets off, python c++ server instead of TMM

updated to work with V2P_rev2
3/19/2015
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
import xml.etree.cElementTree as ElementTree
import threading
import Queue
import time
import json
import vizact
import struct
import math
import array

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN #run world in full screen
)
time.sleep(1)#show off
#set target tolerance for stride length
global targetL
#targetL = 0.562#units are meters
#targetL = 0.429
#targetL = 0.4385
targetL = 0.414
global targetR
#targetR = 0.562
#targetR = 0.429
#targetR = 0.4385
targetR = 0.414

global targettol
targettol = 0.025# 5cm

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =20
#setup array of randomly picked steps
global randy
randy = []
order = [1,2] * STEPNUM
while len(randy) < 100:#optimistically sample the solution space for test orders
    random.shuffle(order)
    if order in randy:
        continue
    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
        randy.append(order[:])
randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
#print(randy)

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxL.setPosition([-0.2,targetL,0.05])
boxL.visible(0)#hide the targets

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxR.setPosition([0.2,targetR,.05])
boxR.visible(0)#hide the targets in this script

viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[.4,0,0],scale=[0.1,0.1,0.1])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-.46,0,0],scale=[0.1,0.1,0.1])

global Rhits
Rhits = [0] * STEPNUM #pre-allocate a list to keep track of the steps, will be used at the end to calculate the targets and tolerances
global Lhits
Lhits = [0] * STEPNUM
global stepind #this keeps track of the total # of attempts
stepind = 0

global RightBeltSpeed
global LeftBeltSpeed
RightBeltSpeed = 0
LeftBeltSpeed = 0

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])
cursorR.visible(0)

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])
cursorL.visible(0)

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.08,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.08,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global histR
histzR = 0

global histL
histzL = 0

global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)

HistBallL.visible(0)
HistBallR.visible(0)

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

def UpdateViz(root,q,speedlist,qq,savestring,q3):
	
	while not endflag.isSet():
		global ballR
		global ballL
		global HistBallR
		global histzR
		global HistBallL
		global histzL
		global boxL
		global boxR
		global targettol
		global target
		global steplengthL
		global steplengthR
		global neutralL
		global neutralR
		global randy
		global stepind #this keeps track of the total # of attempts
		global RightBeltSpeed
		global LeftBeltSpeed
		global Rattempts
		global Lattempts
		global Rhits
		global Lhits

		root = q.get()#look for the next frame data in the thread queue
		if root is None:
			continue
		else:
			#find the data we need from the frame packet
			lp1 = root.find(".//FP_0/SubF_7/Fz")#Left Treadmill
			rp1 = root.find(".//FP_1/SubF_7/Fz")#Right Treadmill
			s0ranky = root.find(".//Sub0/RANK/Y")
			s0lanky = root.find(".//Sub0/LANK/Y")
			
			fn = root.find(".//FN")#find the frame number
			fnn = fn.attrib.values()

			temp = rp1.attrib.values()
			Rz = float(temp[0])#cast forceplate data as float
			temp1 = lp1.attrib.values()
			Lz = float(temp1[0])
			temp4 = s0ranky.attrib.values()
			RANKY = float(temp4[0])/1000
			temp5 = s0lanky.attrib.values()
			LANKY = float(temp5[0])/1000
			
#			cursorR.setScale(0.1,LANKY-RANKY,0.01250)
#			cursorL.setScale(-0.1,RANKY-LANKY,0.01250)
			
#			if (LANKY-RANKY < 0):
#				cursorR.visible(0)
#				neutralR.visible(1)
#			else:
##				cursorR.visible(1)
#				neutralR.visible(0)
#				
#			if (RANKY-LANKY < 0):
#				cursorL.visible(0)
#				neutralL.visible(1)
#			else:
##				cursorL.visible(1)
#				neutralL.visible(0)

			if (Rz < -30) & (histzR >= -30):#RHS condition
				stepind = stepind+1
				Rattempts = Rattempts+1
				HistBallR.setPosition([0.2,LANKY-RANKY, 0])
				
				rightcounter.message(str(Rattempts))#display how many steps have been taken
				try:
					Rhits[Rattempts-1] = LANKY-RANKY#keep record in the list
				except:
					print("Too many Right attempts made")
				neutralL.visible(0)
				neutralR.visible(0)
			if (Lz < -30) & (histzL >= -30):#LHS condition
				stepind = stepind+1
				Lattempts = Lattempts+1
				HistBallL.setPosition([-0.2,RANKY-LANKY, 0])
				
				leftcounter.message(str(Lattempts))#display how many steps have been taken
				try:
					Lhits[Lattempts-1] = RANKY-LANKY#keep record in the list
				except:
					print("Too mane Left attempts made")
				neutralL.visible(0)
				neutralR.visible(0)
			
			if (Rz < -50) & (LANKY-RANKY > 0.04):#check to see if the treadmill needs to move the feet back to neutral
				speedlist = [200,0,1000,1000,0]
				qq.put(speedlist)
			elif (Lz < -50) & (RANKY-LANKY > 0.04):
				speedlist = [0,200,1000,1000,0]
				qq.put(speedlist)
			else:
				speedlist = [0,0,1000,1000,0]
				qq.put(speedlist)
				try:
					if (randy[stepind]  == 1):#when the feet are back together, display the new target
						neutralR.visible(1)
						neutralL.visible(0)
					else:
						neutralR.visible(0)
						neutralL.visible(1)
				except:#executes when stepind is out of range of the size of randy
					print("Required # of steps complete!")
#					break#? not sure what this will do just yet...
			histzR = Rz
			histzL = Lz
			#save data
			savestring = [int(fnn[0]),Rz,Lz,RANKY-LANKY,LANKY-RANKY]#organize the data to be written to file
			q3.put(savestring)
			
	#calculate the mean step length and stdev and print it
	print("Rhits ",Rhits)
	print("Lhits ",Lhits)
	meanstepR = sum(Rhits)/len(Rhits)
	variance = map(lambda x: (x - meanstepR)**2, Rhits)
	stdevR = math.sqrt(sum(variance)/len(variance))
	
	meanstepL = sum(Lhits)/len(Lhits)
	variance = map(lambda x: (x - meanstepL)**2, Lhits)
	stdevL = math.sqrt(sum(variance)/len(variance))
	print 'The average R step length is:'
	print str(meanstepR)
	print 'The R standard deviation is:'
	print str(stdevR)
	
	print 'The average L step length is:'
	print str(meanstepL)
	print 'The L standard deviation is:'
	print str(stdevL)
#	q3.join()
	print("All data has been processed")
	
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

	while not endflag.isSet():
		
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
	#at the end make sure the treadmill is stopped
	out = serializepacket(0,0,500,500,0)
	s2.send(out)
	s2.close()
	
def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'V3FINDTARGETS.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','Rgamma','Lgamma'],file)
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
	t1.join(5)
	t2.join(5)
	t3.join(5)
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
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	
=======
﻿""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing plugin gait with hip marker set.

In version 3 FINDTARGETS rev3, feedback, cursor, on, targets off, python c++ server instead of TMM

updated to work with V2P_rev2
3/19/2015
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
import xml.etree.cElementTree as ElementTree
import threading
import Queue
import time
import json
import vizact
import struct
import math
import array

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN #run world in full screen
)
time.sleep(1)#show off
#set target tolerance for stride length
global targetL
#targetL = 0.562#units are meters
#targetL = 0.429
#targetL = 0.4385
targetL = 0.414
global targetR
#targetR = 0.562
#targetR = 0.429
#targetR = 0.4385
targetR = 0.414

global targettol
targettol = 0.025# 5cm

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =20
#setup array of randomly picked steps
global randy
randy = []
order = [1,2] * STEPNUM
while len(randy) < 100:#optimistically sample the solution space for test orders
    random.shuffle(order)
    if order in randy:
        continue
    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
        randy.append(order[:])
randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
#print(randy)

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxL.setPosition([-0.2,targetL,0.05])
boxL.visible(0)#hide the targets

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxR.setPosition([0.2,targetR,.05])
boxR.visible(0)#hide the targets in this script

viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[.4,0,0],scale=[0.1,0.1,0.1])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-.46,0,0],scale=[0.1,0.1,0.1])

global Rhits
Rhits = [0] * STEPNUM #pre-allocate a list to keep track of the steps, will be used at the end to calculate the targets and tolerances
global Lhits
Lhits = [0] * STEPNUM
global stepind #this keeps track of the total # of attempts
stepind = 0

global RightBeltSpeed
global LeftBeltSpeed
RightBeltSpeed = 0
LeftBeltSpeed = 0

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])
cursorR.visible(0)

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])
cursorL.visible(0)

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.08,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.08,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global histR
histzR = 0

global histL
histzL = 0

global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)

HistBallL.visible(0)
HistBallR.visible(0)

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

def UpdateViz(root,q,speedlist,qq,savestring,q3):
	
	while not endflag.isSet():
		global ballR
		global ballL
		global HistBallR
		global histzR
		global HistBallL
		global histzL
		global boxL
		global boxR
		global targettol
		global target
		global steplengthL
		global steplengthR
		global neutralL
		global neutralR
		global randy
		global stepind #this keeps track of the total # of attempts
		global RightBeltSpeed
		global LeftBeltSpeed
		global Rattempts
		global Lattempts
		global Rhits
		global Lhits

		root = q.get()#look for the next frame data in the thread queue
		if root is None:
			continue
		else:
			#find the data we need from the frame packet
			lp1 = root.find(".//FP_0/SubF_7/Fz")#Left Treadmill
			rp1 = root.find(".//FP_1/SubF_7/Fz")#Right Treadmill
			s0ranky = root.find(".//Sub0/RANK/Y")
			s0lanky = root.find(".//Sub0/LANK/Y")
			
			fn = root.find(".//FN")#find the frame number
			fnn = fn.attrib.values()

			temp = rp1.attrib.values()
			Rz = float(temp[0])#cast forceplate data as float
			temp1 = lp1.attrib.values()
			Lz = float(temp1[0])
			temp4 = s0ranky.attrib.values()
			RANKY = float(temp4[0])/1000
			temp5 = s0lanky.attrib.values()
			LANKY = float(temp5[0])/1000
			
#			cursorR.setScale(0.1,LANKY-RANKY,0.01250)
#			cursorL.setScale(-0.1,RANKY-LANKY,0.01250)
			
#			if (LANKY-RANKY < 0):
#				cursorR.visible(0)
#				neutralR.visible(1)
#			else:
##				cursorR.visible(1)
#				neutralR.visible(0)
#				
#			if (RANKY-LANKY < 0):
#				cursorL.visible(0)
#				neutralL.visible(1)
#			else:
##				cursorL.visible(1)
#				neutralL.visible(0)

			if (Rz < -30) & (histzR >= -30):#RHS condition
				stepind = stepind+1
				Rattempts = Rattempts+1
				HistBallR.setPosition([0.2,LANKY-RANKY, 0])
				
				rightcounter.message(str(Rattempts))#display how many steps have been taken
				try:
					Rhits[Rattempts-1] = LANKY-RANKY#keep record in the list
				except:
					print("Too many Right attempts made")
				neutralL.visible(0)
				neutralR.visible(0)
			if (Lz < -30) & (histzL >= -30):#LHS condition
				stepind = stepind+1
				Lattempts = Lattempts+1
				HistBallL.setPosition([-0.2,RANKY-LANKY, 0])
				
				leftcounter.message(str(Lattempts))#display how many steps have been taken
				try:
					Lhits[Lattempts-1] = RANKY-LANKY#keep record in the list
				except:
					print("Too mane Left attempts made")
				neutralL.visible(0)
				neutralR.visible(0)
			
			if (Rz < -50) & (LANKY-RANKY > 0.04):#check to see if the treadmill needs to move the feet back to neutral
				speedlist = [200,0,1000,1000,0]
				qq.put(speedlist)
			elif (Lz < -50) & (RANKY-LANKY > 0.04):
				speedlist = [0,200,1000,1000,0]
				qq.put(speedlist)
			else:
				speedlist = [0,0,1000,1000,0]
				qq.put(speedlist)
				try:
					if (randy[stepind]  == 1):#when the feet are back together, display the new target
						neutralR.visible(1)
						neutralL.visible(0)
					else:
						neutralR.visible(0)
						neutralL.visible(1)
				except:#executes when stepind is out of range of the size of randy
					print("Required # of steps complete!")
#					break#? not sure what this will do just yet...
			histzR = Rz
			histzL = Lz
			#save data
			savestring = [int(fnn[0]),Rz,Lz,RANKY-LANKY,LANKY-RANKY]#organize the data to be written to file
			q3.put(savestring)
			
	#calculate the mean step length and stdev and print it
	print("Rhits ",Rhits)
	print("Lhits ",Lhits)
	meanstepR = sum(Rhits)/len(Rhits)
	variance = map(lambda x: (x - meanstepR)**2, Rhits)
	stdevR = math.sqrt(sum(variance)/len(variance))
	
	meanstepL = sum(Lhits)/len(Lhits)
	variance = map(lambda x: (x - meanstepL)**2, Lhits)
	stdevL = math.sqrt(sum(variance)/len(variance))
	print 'The average R step length is:'
	print str(meanstepR)
	print 'The R standard deviation is:'
	print str(stdevR)
	
	print 'The average L step length is:'
	print str(meanstepL)
	print 'The L standard deviation is:'
	print str(stdevL)
#	q3.join()
	print("All data has been processed")
	
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

	while not endflag.isSet():
		
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
	#at the end make sure the treadmill is stopped
	out = serializepacket(0,0,500,500,0)
	s2.send(out)
	s2.close()
	
def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'V3FINDTARGETS.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','Rgamma','Lgamma'],file)
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
	t1.join(5)
	t2.join(5)
	t3.join(5)
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
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	
>>>>>>> origin/master
