﻿#script runs biofeedback routine with python c++ server

#revision 7    2/19/2015   WDA

import socket
import sys
import io
import re
from xml.etree import ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN #run world in full screen
)

#indicate flag for post-catch targets, which last for the first 12 steps
global catchflag
catchflag = 0
global stridecounter
stridecounter = 0

#set target tolerance for stride length
global targetL
targetL = 0.213
global targetR
targetR = 0.2405

#R Rigth leg 
global R
R = 1.3094
#R left leg
global R2
R2 = 1.5252

global targettol
targettol = 0.025

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.005])
boxL.setPosition([-0.2,targetL,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.005])
boxR.setPosition([0.2,targetR,0])

viz.MainView.setPosition(0, 0.25, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels to count successful steps taken
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[4.6,3*targetR,12])
#rightcounter.visible(0)
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-5.5,3*targetL,12])
#leftcounter.visible(0)

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])

global HistBallR
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.2,0.01,0.0125], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.alpha(0.8)

global histzR
histzR = 0
global histzL
histzL = 0

global HistBallL
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.2,0.01,0.0125], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

global psudoR
global psudoL
	
psudoR = 0
psudoL = 0

global Rtop
global Rhsp
global Ltop
global Lhsp

Ltop = 0
Lhsp = 0
Rtop = 0
Rhsp = 0

#keep track of each step, whether it is good or bad
global Rgorb
global Lgorb
Rgorb = 0
Lgorb = 0

global RHS
global LHS
RHS = 0
LHS = 0

global FNold
FNold = 0
global repeatcount
repeatcount = 0

def UpdateViz(root,q,savestring,q3):
#	timeold = time.time()
	
	while not endflag.isSet():
		global cursorR
		global cursorL
		global HistBallR
		global histzR
		global HistBallL
		global histzL
		global boxL
		global boxR
		global targettol
		global targetR
		global targetL
		global steplengthL
		global steplengthR
		global psudoR
		global psudoL
		global RCOUNT
		global LCOUNT
		global Rtop
		global Rhsp
		global Ltop
		global Lhsp
		global catchflag
		global stridecounter
		global Rgorb
		global Lgorb
		global R
		global R2
		global RHS
		global LHS
		
		#get some data
		root = q.get()
		
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
		temp2 = s0rhipy.attrib.values()
		RHIPY = float(temp2[0])/1000 #convert to meters
		temp3 = s0lhipy.attrib.values()
		LHIPY = float(temp3[0])/1000
		temp4 = s0ranky.attrib.values()
		RANKY = float(temp4[0])/1000
		temp5 = s0lanky.attrib.values()
		LANKY = float(temp5[0])/1000
		
		cursorR.setScale(0.1,RHIPY-RANKY,0.01250)
		cursorL.setScale(-0.1,LHIPY-LANKY,0.01250)
		
		#determine if we need to hide the cursor
		if (RHIPY-RANKY < 0) | (Rz < -30):
			cursorR.visible(0)
		else:
			cursorR.visible(1)
		if (LHIPY-LANKY < 0) | (Lz < -30):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
	
		if (Rz <= -30) & (histzR > -30): #RHS condition
			HistBallR.setPosition([0.2,RHIPY-RANKY, 0])#update yellow history ball when HS happens
			steplengthR = RHIPY-RANKY
			stridecounter = stridecounter+1  #this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
			Rhsp = RHIPY-RANKY
			psudoR = psudoR +1
			RHS = 1
			#if successful step was taken, keep track of it
			if (abs(steplengthR-targetR) <= targettol):
				RCOUNT = RCOUNT+1
				rightcounter.message(str(RCOUNT))
				Rgorb = 1  #flag this step as good or bad
			else:
				Rgorb = 0
			if (catchflag == 1) & (stridecounter > 12):
				boxR.setPosition([0.2,targetR,0])
			elif (catchflag == 1) & (stridecounter <= 12):
				boxR.setPosition([0.2,0.31,0])
			else:
				boxR.setPosition([0.2,targetR,0])
#			print(histR)
		elif (Rz > -30) & (histzR < -30):#RTO
			#calculate Toe-Off position
			Rtop = RHIPY-RANKY
			RHS = 0
			if (psudoR >= 5): #if it's time to update target value
#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
				targetR = abs(Rhsp)+(1/(1+R))*(abs(Rtop)-(R*abs(Rhsp)))
#				targetR = Rhsp+1/(1+R)*(abs(Rtop)+R*abs(Rhsp))
#				targetR = 1/(1+R)*(abs(Rtop)+R*abs(Rhsp))
				print('targetR')
				print(targetR)
				psudoR = 1
				boxR.setPosition([0.2,targetR,0])
#			else:
#				print("psudoR out of range")
		else:
			RHS = 0
			
		if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit
			boxR.color( viz.WHITE )
		else:
			boxR.color( viz.BLUE )
			
		if (Lz < -30) & (histzL > -30): #RHS condition
			HistBallL.setPosition([-0.2,LHIPY-LANKY, 0])#update yellow history ball when HS happens
			steplengthL = LHIPY-LANKY
			stridecounter = stridecounter+1  #this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
			Lhsp = LHIPY-LANKY
			psudoL = psudoL +1
			LHS = 1
			#if successful step was taken, keep track of it
			if (abs(steplengthL-targetL) <= targettol):
				LCOUNT = LCOUNT+1
				leftcounter.message(str(LCOUNT))
				Lgorb = 1  #flag this step as good or bad
			else:
				Lgorb = 0
			if (catchflag == 1) & (stridecounter > 12):
				boxL.setPosition([-0.2,targetL,0])
			elif (catchflag == 1) & (stridecounter <= 12):
				boxL.setPosition([-0.2,0.31,0])
			else:
				boxL.setPosition([-0.2,targetL,0])
		elif (Lz > -30) & (histzL < -30):#LTO
			#calculate Toe-Off position
			Ltop = LHIPY-LANKY
			LHS = 0
			if (psudoL >= 5): #if it's time to update target value
#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
				targetL = abs(Lhsp)+(1/(1+R2))*(abs(Ltop)-(R2*abs(Lhsp)))
#				targetR = Rhsp+1/(1+R)*(abs(Rtop)+R*abs(Rhsp))
#				targetR = 1/(1+R)*(abs(Rtop)+R*abs(Rhsp))
				print('targetL')
				print(targetL)
				psudoL = 1
				boxL.setPosition([-0.2,targetL,0])
#			else:
#				print("psudoL out of range")
		else:
			LHS = 0
		if (abs(steplengthL-targetL) <= targettol):#highlight the target when the target is hit
			boxL.color( viz.WHITE )
		else:
			boxL.color( viz.BLUE )
		
		histzR = Rz
		histzL = Lz

		#send some data to be saved
		fn = root.find(".//FrameNumber")#find the frame number
		fnn = fn.attrib.values()
#		print(fnn[0])

		savestring = [int(fnn[0]),Rz,Lz,RHS,LHS,Rgorb,Lgorb,RHIPY-RANKY,LHIPY-LANKY,targetR,targetL,RHIPY,LHIPY,RANKY,LANKY]#organize the data to be written to file
#		print(sys.getsizeof(savestring))
		q3.put(savestring)

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
		global repeatcount
		global FNold
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
			while (sys.getsizeof(databuf) < nextsize+21):
				data = s.recv(nextsize)#data buffer as a python string
				databuf = databuf + data#collect data into buffer until size is matched
#			print(sys.getsizeof(databuf))
#			print(databuf)
			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			fn = root.find(".//FrameNumber")#find the frame number
			fnn = fn.attrib.values()
			FN = int(fnn[0])
			if (FN == int(FNold)) & (repeatcount > 30):
				print("Repeated Frames more than 30 times")
#				break
			elif (FN == FNold):
				repeatcount = repeatcount+1
#				print("Repeat count is: ",repeatcount)
			else:
				repeatcount = 0
			FNold = FN
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
	mststring = str(mst2)+'DYNTARGSalpha.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RGORB','LGORB','Ralpha','Lalpha','R target','L target','RHIPY','LHIPY','RANKY','LANKY'],file)
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
	t4.join(5)
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
vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	