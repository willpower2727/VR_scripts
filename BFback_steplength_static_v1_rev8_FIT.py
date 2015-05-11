﻿""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing typical plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 1 rev6, feedback, cursor, are off.

Treadmill moves the feet back to neutral after a step

rev 8 introduces the new initial pose where contralateral leg is loaded prior to step
Use V2P R2
3/19/2015 WDA
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
import array
import math
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN #run world in full screen
)
global messagewin
messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)

time.sleep(2)#show off our cool logo, not really required but cool
#set target tolerance for stride length

global targetL
targetL = 0.4

global targetR
targetR = 0.4

global targettol
targettol = 0.025

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM = 10

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

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxL.setPosition([-0.2,targetL,0.05])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxR.setPosition([0.2,targetR,.05])

viz.MainView.setPosition(0, 0.25, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR+0.6,12])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-4.6,targetL+0.6,12])

global rgorb
rgorb = 0 #this will be 0 or 1, depending on success or failure
global lgorb
lgorb = 0
global stepind #this keeps track of the total # of attempts
stepind = 0

global Rattempts
global Lattempts
Rattempts = 0
Lattempts = 0

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

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global histzR
histzR = 0

global histzL
histzL = 0

global steplengthL
steplengthL = 0
global steplengthR
steplengthR = 0

global old0
old0 = 0
global old1
old1 = 0

global Rspeed
global Lspeed
Rspeed = 0
Lspeed = 0

global phaxxe
phaxxe = 1 #don't start at match ankles because there is no previous test to look at, indexing error in stepind


def UpdateViz(root,q,speedlist,qq,savestring,q3):
	
	while not endflag.isSet():
		global ballR
		global ballL
		global histzR
		global histzL
		global boxL
		global boxR
		global targettol
		global target
		global steplengthL
		global steplengthR
		global neutralL
		global neutralR
		global RCOUNT
		global LCOUNT
		global randy
		global Rspeed
		global Lspeed
		global rgorb
		global lgorb
		global stepind
		global Rattempts
		global Lattempts
		global messagewin
		global phaxxe
		
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
			
			#state machine
			if (phaxxe == 0):  #match ankles if needed
#				viz.visible(0)
				try:
					if (randy[stepind-1] == 1) & (randy[stepind] == 1):#previously a right step next is also right
						phaxxe = 1 #proceed
					elif (randy[stepind-1] == 1) & (randy[stepind] == 2): #need to match ankles first!
						#move right ankle to left ankle
						if (Rz < -30) & (Lz < -30) &(LANKY-RANKY >= 0.04):
							Rspeed = 300
						else:
							Rspeed = 0
							phaxxe = 1#proceed
					elif (randy[stepind-1] == 2) & (randy[stepind] == 1): #need to match ankles first
						if (Rz < -30) & (Lz < -30) & (RANKY-LANKY >= 0.04):
							Lspeed = 300
						else:
							Lspeed = 0
							phaxxe = 1#proceed
					elif (randy[stepind-1] == 2) & (randy[stepind] == 2):
						phaxxe = 1#proceed
					messagewin.setText('Preparing for next test \nDo not take a step')
					messagewin.visible(1)
				except:
					messagewin.setText('Test Complete!')
					messagewin.visible(1)
					print('max steps reached')
					
					
			#phase 1 move right leg to position
			elif (phaxxe == 1):
#				viz.visible(0)
				messagewin.setText('Preparing Right Leg \n Do not step')
				messagewin.visible(1)
				#move to the initial pose
				try:
					if (randy[stepind] == 1):#right leg next test
#						if (Rz < -30) & (Lz < -30) & (abs((1.45-targetR)-LANKY) >= 0.04):#left foot is not at start position (1.45-target)
#							Lspeed = int(300*math.copysign(1,(1.45-targetR)-LANKY))
#						else:
#							Lspeed = 0
						if (Rz < -30) & (Lz < -30) & (abs(1.45-RANKY) >= 0.04):#right foot is not at 1.45 m from origin
							Rspeed = int(300*math.copysign(1,1.45-RANKY))
						else:
							Rspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs(1.45-RANKY) <= 0.04):#everything is ready for the left leg to move next
							phaxxe = 2#proceed to move left leg

					elif (randy[stepind] == 2):#left leg next test
						if (Rz < -30) & (Lz < -30) & (abs((1.45-targetR)-RANKY) >= 0.04):#right foot is not at start position (1.45-target)
							Rspeed = int(300*math.copysign(1,(1.45-targetR)-RANKY))
						else:
							Rspeed = 0
#						if (Rz < -30) & (Lz < -30) & (abs(1.45-LANKY) > 0.04):#left foot is not at 1.45 m from origin
#							Lspeed = int(300*math.copysign(1,1.45-LANKY))
#						else:
#							Lspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs((1.45-targetR)-RANKY) <= 0.04):
							phaxxe = 2#proceed to move left leg

				except:
					disp('Max # of steps reached')
					Rspeed = 0
					Lspeed = 0
					boxR.visible(0)
					boxL.visible(0)
					
					
			#phase 2 move left foot
			elif (phaxxe == 2):
				messagewin.setText('Preparing Left Leg \nDo not step')
				messagewin.visible(1)
				try:
					if (randy[stepind] == 1):#right leg next test
						if (Rz < -30) & (Lz < -30) & (abs((1.45-targetR)-LANKY) >= 0.04):#left foot is not at start position (1.45-target)
							Lspeed = int(300*math.copysign(1,(1.45-targetR)-LANKY))
						else:
							Lspeed = 0
#						if (Rz < -30) & (Lz < -30) & (abs(1.45-RANKY) >= 0.04):#right foot is not at 1.45 m from origin
#							Rspeed = int(300*math.copysign(1,1.45-RANKY))
#						else:
#							Rspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs((1.45-targetR)-LANKY) <= 0.04):#everything is ready for the next step so display next target
							phaxxe = 3 #proceed to prep pose

					elif (randy[stepind] == 2):#left leg next test
#						if (Rz < -30) & (Lz < -30) & (abs((1.45-targetR)-RANKY) > 0.04):#right foot is not at start position (1.45-target)
#							Rspeed = int(300*math.copysign(1,(1.45-targetR)-RANKY))
#						else:
#							Rspeed = 0
						if (Rz < -30) & (Lz < -30) & (abs(1.45-LANKY) >= 0.04):#left foot is not at 1.45 m from origin
							Lspeed = int(300*math.copysign(1,1.45-LANKY))
						else:
							Lspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs(1.45-LANKY) <= 0.04):#everything is ready for the next step so display next target
							phaxxe = 3
				except:
					disp('Max # of steps reached')
					Rspeed = 0
					Lspeed = 0
					boxR.visible(0)
					boxL.visible(0)
			
			#phase 3 pre-pose
			elif (phaxxe == 3):
				viz.visible(0)#turn off display
				try:
					if (randy[stepind] == 1):#right leg next test
						messagewin.setText('Shift weight to the Left Leg \nRaise right heel')
						messagewin.visible(1)
						#wait for right heel to come up
						if (Rz/Lz < 0.3):
							boxR.visible(1)
							boxL.visible(0)
							phaxxe = 4#proceed with test
							messagewin.visible(0)
							viz.visible(1)
					elif (randy[stepind] == 2):#left leg next test
						#wait for left heel to come up
						messagewin.setText('Shift weight to the Right Leg \nRaise left heel')
						messagewin.visible(1)
						if (Lz/Rz < 0.3):
							boxR.visible(0)
							boxL.visible(1)
							phaxxe = 4
							messagewin.visible(0)
							viz.visible(1)
							
				except:
					pass #max # of steps reached
			
			#phase 3 attempt
			elif (phaxxe == 4):
				messagewin.visible(0)
#				viz.visible(1)
					
				if (Rz <= -30) & (histzR > -30) & (LANKY-RANKY > targetR/4):#RHS condition
					stepind = stepind+1
					Rattempts = Rattempts+1
					rightcounter.message(str(Rattempts))
	#				HistBallR.setPosition([0.2,LANKY-RANKY, 0])
					if (abs((LANKY-RANKY)-targetR) <= targettol):
						RCOUNT = RCOUNT+1
	#					boxR.color( viz.WHITE )
						rgorb = 1
					else:
	#					boxR.color( viz.BLUE )
						rgorb = 0
					phaxxe = 0
					
				
				if (Lz <= -30) & (histzL > -30):#LHS condition
					stepind = stepind+1
					Lattempts = Lattempts+1
					leftcounter.message(str(Lattempts))
	#				HistBallL.setPosition([-0.2,RANKY-LANKY, 0])
					if (abs((RANKY-LANKY)-targetL) <= targettol):
						LCOUNT = LCOUNT+1
	#					boxL.color( viz.WHITE )
						lgorb = 1
					else:
	#					boxL.color( viz.BLUE )
						lgorb = 0
					phaxxe = 0

			else:
				disp('Warning phase value un-defined')		
				
			#send speed update
			speedlist = [Rspeed,Lspeed,1200,1200,0]#the accelerations "1200 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
			qq.put(speedlist)
			
			histzR = Rz
			histzL = Lz
			#save data
			savestring = [int(fnn[0]),Rz,Lz,rgorb,lgorb,RANKY-LANKY,LANKY-RANKY,targetR-(LANKY-RANKY),targetL-(RANKY-LANKY)]#organize the data to be written to file
			q3.put(savestring)
#			timeold = time.time()
	
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
	mststring = str(mst2)+'V1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RGORB','LGORB','Rgamma','Lgamma','Rerror','Lerror'],file)
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
		
	file.close()
#	q3.join()
	print("savedata finished writing")
	
endflag = threading.Event()#an event to raise when we are ready to stop recording
def raisestop(sign):
	#the sign passed in doesn't do anything, I just didn't know how to make this work without passing something in...
	print("stop flag raised")
	endflag.set()
	t1.join()
	t2.join()
	t3.join()
	t4.join()
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

vizact.onkeydown('q',raisestop,'t')#biggle is meaningless, just need to pass something into the raisestop callback
