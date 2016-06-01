""" Biofeedback routine used to train subjects to take a step forward of various length
V4 uses a compound method to test how subjects step. Initially, both feet are together in the Y direction. step length is tested in a compound manner meaning that
the leg not being tested is also moved. The flow is this: subject stands with both feet together. Subject takes a step forward with the un-testing leg, then with the testing leg, in a fluid manner
Hopefully this will capture the coupled nature of how perception of step length during adaptation is changed.

In version 4 feedback, cursor, and target are on.
rev1 

#Use with V2P R3
wda 4/10/2015
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
#import xml.etree.cElementTree as ElementTree
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
time.sleep(2)#show off our cool logo, not really required but cool
global messagewin
messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)

#messagewin.visible(0)
#set target tolerance for stride length
global targetXl
targetXl =0.5966
global targetXr
targetXr = 0.5845
global targetUl
targetUl =0.5966
global targetUr
targetUr = 0.5845

global targettol
targettol = 0.0375# 5cm total

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =10
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
boxL = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.2,0.005,targettol*2])
boxL.setPosition([-0.2,targetXl,0])
boxL.setEuler(0,90,0)
global boxR
boxR = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.2,0.005,targettol*2])
boxR.setPosition([0.2,targetXr,0])
boxR.setEuler(0,90,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0

rightcounter = viz.addText(str(RCOUNT),pos=[0.4,0,0],scale=[0.1,0.1,0.1])
leftcounter = viz.addText(str(LCOUNT),pos=[-0.6,0,0],scale=[0.1,0.1,0.1])

global RGOB
RGOB = 0 #this will be 0 or 1, depending on success or failure
global LGOB
LGOB = 0
global stepind #this keeps track of the total # of attempts
stepind = 0

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,targetXr,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,targetXl,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global HistBallR
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetXr,0])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)
HistBallR.visible(0)

global HistBallL
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetXl,0])
HistBallL.alpha(0.8)
HistBallL.visible(0)

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

global rgorb
global lgorb
rgorb = 0
lgorb = 0

global flagRHS
global flagLHS
flagRHS = 0
flagLHS = 0

global repeatcount
repeatcount = 0

global Rspeed
global Lspeed
Rspeed = 0
Lspeed = 0

global phaxxe
phaxxe = 2 #don't start at match ankles because there is no previous test to look at, indexing error in stepind

#global speedlist
#speedlist = [0,0,0,0,0]

viz.MainView.setPosition(0, 0.6, -2)
viz.MainView.setEuler(0,0,0)

def UpdateViz(root,q,speedlist,qq,savestring,q3):

	while not endflag.isSet():
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
		global rgorb
		global lgorb
		global Rspeed
		global Lspeed
		global phaxxe
		global messagewin
		global flagLHS
		global flagRHS
		
		
		root = q.get()#look for the next frame data in the thread queue
		if root is None:
			continue
		else:
			tempdat = root.split(',')
			FN = int(tempdat[0])
			Rz = float(tempdat[3])
			Lz = float(tempdat[2])
			RHIPY = float(tempdat[4])/1000
			LHIPY = float(tempdat[5])/1000
			RANKY = float(tempdat[6])/1000
			LANKY = float(tempdat[7])/1000
			#find the data we need from the frame packet
#			lp1 = root.find(".//FP_0/SubF_7/Fz")#Left Treadmill
#			rp1 = root.find(".//FP_1/SubF_7/Fz")#Right Treadmill
#			s0ranky = root.find(".//Sub0/RANK/Y")
#			s0lanky = root.find(".//Sub0/LANK/Y")
##			s0rheelz = root.find(".//Sub0/RHEEL/Z")
##			s0lheelz = root.find(".//Sub0/LHEEL/Z")
#			
#			fn = root.find(".//FN")#find the frame number
#			fnn = fn.attrib.values()
#
#			temp = rp1.attrib.values()
#			Rz = float(temp[0])#cast forceplate data as float
#			temp1 = lp1.attrib.values()
#			Lz = float(temp1[0])
#			temp4 = s0ranky.attrib.values()
#			RANKY = float(temp4[0])/1000#convert to m
#			temp5 = s0lanky.attrib.values()
#			LANKY = float(temp5[0])/1000
			
			#state machine
			if (phaxxe == 0): #move the leg furthest away
				messagewin.setText('Moving...')
				messagewin.visible(1)
				#move to the initial pose
				try:
					if (randy[stepind-1] == 1):#previous test was right leg, move right leg first 
						if (Rz<-30) & (Lz<-30) & (abs(1.45-RANKY) >= 0.04):
							Rspeed = 300
						elif (abs(1.45-RANKY) < 0.04):
							Rspeed = 0
							phaxxe = 1
#							print('previous target was R, phase = ',phaxxe)
#							boxR.color( viz.BLUE)
#							boxL.color( viz.BLUE)
							boxR.visible(0)#hide the targets
							boxL.visible(0)
							boxR.color( viz.BLUE)
							boxL.color( viz.BLUE)
							HistBallL.visible(0)
							HistBallR.visible(0)
						else:
							Rspeed = 0
							print('Balance loss detected, stopped')
					elif (randy[stepind-1] == 2):
						if (Rz<-30) & (Lz<-30) & (abs(1.45-LANKY) >= 0.04):
							Lspeed = 300
						elif (abs(1.45-LANKY) < 0.04):
							Lspeed = 0
							phaxxe = 1
							boxR.visible(0)
							boxL.visible(0)
							boxR.color( viz.BLUE)
							boxL.color( viz.BLUE)
							HistBallL.visible(0)
							HistBallR.visible(0)
#							print('previous target was L, phase = ',phaxxe)
						else:
							Lspeed = 0
#							print('Balance loss detected, stopped')
				except:
					disp('Max # of steps reached?')
					Rspeed = 0
					Lspeed = 0
					boxR.visible(0)
					boxL.visible(0)
			elif (phaxxe == 1): #move the other leg
#				viz.visible(0)
				messagewin.setText('Moving...')
				#move to the initial pose
				try:
					if (randy[stepind-1] == 1):#previous test was right leg, move right leg first 
						if (Rz<-30) & (Lz<-30) & (abs(1.45-LANKY) >= 0.04):
							Lspeed = 300
						else:
							Lspeed = 0
							phaxxe = 2
					elif (randy[stepind-1] == 2):
						if (Rz<-30) & (Lz<-30) & (abs(1.45-RANKY) > 0.04):
							Rspeed = 300
						else:
							Rspeed = 0
							phaxxe = 2
				except:
					disp('Max # of steps reached?')
					Rspeed = 0
					Lspeed = 0
					boxR.visible(0)
					boxL.visible(0)	
			elif (phaxxe == 2):#display the targets
				try:
					if (randy[stepind] == 1):
						boxR.setPosition([0.2,targetXl+targetUr,0])
						boxL.setPosition([-0.2,targetXl,0])
						boxR.visible(1)
						boxL.visible(1)
						neutralR.setScale([0.1,0.0125,0.0125])
						neutralL.setScale([0.1,3*0.0125,0.0125])
						phaxxe = 3
					elif (randy[stepind] == 2):
						boxR.setPosition([0.2,targetXr,0])
						boxL.setPosition([-0.2,targetUl+targetXr,0])
						boxR.visible(1)
						boxL.visible(1)
						neutralR.setScale([0.1,3*0.0125,0.0125])
						neutralL.setScale([0.1,0.0125,0.0125])
						phaxxe = 3
				except:
					continue
			elif (phaxxe == 3):#time for an attempt
				messagewin.visible(0)
#				viz.visible(1)
				try:
					if (randy[stepind] == 1):
#						cursorR.setPosition([0.2,targetL,0.025])
						cursorR.visible(0)
#						cursorL.setPosition([-0.2,0,0.025])
						if (LANKY-RANKY < 0.04):
							cursorR.visible(0)
							cursorL.visible(1)
							cursorL.setScale(0.1,RANKY-LANKY,0.01250)
						else:
							cursorR.visible(1)
							cursorL.visible(0)
							cursorR.setScale(0.1,1.45-LANKY+LANKY-RANKY,0.01250)
#						cursorL.visible(0)
					elif (randy[stepind] == 2):
#						cursorL.setPosition([-0.2,targetR,0.025])
						cursorL.visible(0)
#						cursorR.setPosition([0.2,0,0.025])
						if (RANKY-LANKY < 0.04):
							cursorL.visible(0)
							cursorR.visible(1)
							cursorR.setScale(0.1,LANKY-RANKY,0.01250)
						else:
							cursorL.visible(1)
							cursorR.visible(0)
#							cursorL.setScale(0.1,targetXl+RANKY-LANKY,0.01250)
							cursorL.setScale(0.1,1.45-RANKY+RANKY-LANKY,0.01250)
#						cursorR.visible(0)
				except:
					pass
					
				if (Rz <= -30) & (histzR > -30):#RHS condition
#					stepind = stepind+1
					Rattempts = Rattempts+1
					cursorR.visible(0)#turn off the cursor
#					cursorL.visible(1)
					if (randy[stepind] == 1):
						HistBallR.setPosition([0.2,LANKY-RANKY+1.45-LANKY, 0])
						if (abs((LANKY-RANKY)-targetUr) <= targettol):
							RCOUNT = RCOUNT+1
							boxR.color( viz.WHITE )
							rgorb = 1
						else:
							boxR.color( viz.BLUE )
							rgorb = 0
					elif (randy[stepind] == 2):
						cursorL.visible(1)
						boxL.setPosition([-0.2,targetUl+1.45-RANKY,0])
						HistBallR.setPosition([0.2,LANKY-RANKY, 0])
						if (abs((LANKY-RANKY)-targetXr) <= targettol):
							RCOUNT = RCOUNT+1
							boxR.color( viz.WHITE )
							rgorb = 1
						else:
							boxR.color( viz.BLUE )
							rgorb = 0
					HistBallR.visible(1)
					rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
					flagRHS = 1

				if (Lz <= -30) & (histzL > -30):#LHS condition
#					stepind = stepind+1
					Lattempts = Lattempts+1
					cursorL.visible(0)
#					cursorR.visible(1)
					if (randy[stepind] == 1):
						cursorR.visible(1)
						boxR.setPosition([0.2,1.45-LANKY+targetUr,0])
						HistBallL.setPosition([-0.2,RANKY-LANKY, 0])
						if (abs((RANKY-LANKY)-targetXl) <= targettol):
							LCOUNT = LCOUNT+1
							boxL.color( viz.WHITE )
							lgorb = 1
						else:
							boxL.color( viz.BLUE )
							lgorb = 0
					elif (randy[stepind] == 2):
						HistBallL.setPosition([-0.2,RANKY-LANKY+1.45-RANKY, 0])
						if (abs((RANKY-LANKY)-targetUl) <= targettol):
							LCOUNT = LCOUNT+1
							boxL.color( viz.WHITE )
							lgorb = 1
						else:
							boxL.color( viz.BLUE )
							lgorb = 0
					HistBallL.visible(1)
					leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
					flagLHS = 1
				
				if flagRHS & flagLHS:#signal to start next phase after both HS
					phaxxe = 0
					flagRHS = 0
					flagLHS = 0
					cursorL.visible(0)
					cursorR.visible(0)
					stepind  =stepind+1
			else:
				disp('Warning phase value un-defined')

				
			#send speed update
			speedlist = [Rspeed,Lspeed,1300,1300,0]#the accelerations "1300 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
			qq.put(speedlist)
			
			histzR = Rz
			histzL = Lz
			#save data
			try:
				savestring = [FN,Rz,Lz,rgorb,lgorb,RANKY-LANKY,LANKY-RANKY,targetXr-(LANKY-RANKY),targetXl-(RANKY-LANKY),targetUr-(LANKY-RANKY),targetUl-(RANKY-LANKY),randy[stepind]]#organize the data to be written to file
			except:
				print('stepind out of range')
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
#		global FNold
#		global repeatcount
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
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			root = databuf
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
	mststring = str(mst2)+'V4.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RGORB','LGORB','Rgamma','Lgamma','Xrerror','XLerror','Urerror','Ulerror','test'],file)
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
#			break
			print("data finished write to file")
			break
		else:
			json.dump(savestring, file)
			print("data still writing to file")
		
#	print("savedata finished writing")
	file.close()
	print("savedata finished writing")
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
	
