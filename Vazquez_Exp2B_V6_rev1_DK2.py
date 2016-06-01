#Exp2B V6 alteration of "Perceptual Sensory Correlates of Split Belt Walking Adaptation"
#
#
#Subjects perform 30 stepping trials on each leg, they try to match anterior hip-ankle distance at HS with the left or "slow" leg HS. 
#targets are displayed on a latitudinal grid, 20 targets, 2 cm apart. The left leg target appears as a red circle.The legs start tied, 
#the subject takes a step with each leg, then the treadmill moves them back
#
#V6 is the evaluation of V5, two step
#
#V2P_DK2_R1
#
#William Anderton 2/12/2016

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
import threading
import Queue
import time
import json
import vizact
import struct
import array
import math
import subprocess
import win32gui
import numpy as np
import imp
oculus = imp.load_source('oculus', 'C:\Program Files\WorldViz\Vizard5\python\oculus.py')
import vizlens

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
viz.go(
#viz.FULLSCREEN #run world in full screen
)
time.sleep(1)#show off our cool logo, not really required but cool

global hmd
hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')
else:
	profile = hmd.getProfile()
	if profile:
		hmd.setIPD(profile.ipd)
	
global messagewin
#messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)
messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_CENTER,fontSize=60,icon=False,key=None)

#global targetCENTER
#targetCENTER = 0.21

global targetL
targetL = 0.2783141

global targetR
targetR = targetL

global targettol
targettol = 0.02

global circleL #slow leg circle marker
circleL = vizshape.addSphere(0.01,50,50,color=viz.RED)
circleL.setPosition(-0.03,targetL,0)
circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global circleR #slow leg circle marker
circleR = vizshape.addSphere(0.01,50,50)
circleR.color(1,0.7,0)
circleR.setPosition(0.04,targetR,0)
circleR.disable(viz.LIGHTING)#no shading, we don't want depth perception here

#prompt bars
global neutralR
neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.05,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.06,-0.02,0])
neutralR.disable(viz.LIGHTING)
neutralR.visible(0)#to start

global neutralL
neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.05,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.05,-0.02,0])
neutralL.disable(viz.LIGHTING)
neutralL.visible(0)

#create latitudinal grid
lines = {}#create empty dictionary
for x in range(1,23,1):
	lines["T{0}".format(x)]=vizshape.addBox(size=[1,0.001,0.001])
	lines["T{0}".format(x)].setPosition(0,(x-1)*0.02,0)
#	print((x-1)*0.02)
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	

viz.MainView.setPosition(0, 0.25, -0.55)
viz.MainView.setEuler(0,0,0)

global histzR
histzR = -500
global histzL
histzL = -500

global rgorb
rgorb = 0
global lgorb
lgorb = 0

global Rerror
Rerror = 0
global Lerror
Lerror = 0

global RHS
RHS = 0
global LHS
LHS = 0

global phase
phase = 0#don't start at moving feet

global Ralpha
Ralpha = 0
global Lalpha
Lalpha = 0

#initialize the order of tests, for now, only the right side will be tested
global STEPNUM
STEPNUM =8
#setup array of randomly picked steps
global randy
randy = []
order = [1,2] * STEPNUM#change this line to add in left tests
while len(randy) < 10:#optimistically sample the solution space for test orders
    random.shuffle(order)
    if order in randy:
        continue
    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
        randy.append(order[:])
randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
#print(randy)

def updatetargetdisplay(ts,vizobj,flag,flag2):  #distance value, circle object, flag=1 for left, anything else for right
	#flag2 signifies if the highlighted number needs to change
	
	global tnums
#	print(tnums)
	#figure out which target to place circle in and highlight the number
	ts = abs(ts)*100 #convert units to centimeters for rounding
#	print("ts",ts)
	oddnum = np.floor(ts / 2.) * 2 + 1 #round to the nearest odd integer
#	print("oddnum",int(oddnum))
	index = int((oddnum-1)/2)
#	print("index",index)
	if (flag2 == 1):
		#turn the other target numbers back to white
		for i in [x for x in xrange(21) if x != int(index)]:
			tnums["Num{0}".format(i)].color(viz.WHITE)
		#highlight the selected target
		try:
			tnums["Num{0}".format(int(index))].color(viz.RED)
		except:
			pass
	else:
		pass
	
	#update position of circle
#	vizobj.setPosition(-0.1,oddnum/100,0)
	if (flag == 1):
#		vizobj.setPosition(-0.1,ts/100,0) #analog placement
		vizobj.setPosition(-0.03,oddnum/100,0)#discrete placement
	else:
#		vizobj.setPosition(0.1,ts/100,0) #analog placement
		vizobj.setPosition(0.04,oddnum/100,0) #discrete placement
		
	return index #return in units of meters
	
global targetnum
targetnum = updatetargetdisplay(targetL,circleL,1,1)
nothing = updatetargetdisplay(targetR,circleR,2,2)

circleL.visible(0)#turn off markers
circleR.visible(0)

global flagRHS
flagRHS = 0
global flagLHS
flagLHS = 0

global Rspeed
Rspeed = 0
global Lspeed
Lspeed = 0

global old0
old0 = 0
global old1
old1 = 0

global stepind #this keeps track of the total # of attempts
stepind = 1
	

def UpdateViz(root,q,speedlist,qq,savestring,q3):

	global histzL
	global histzR
	global targetL
	global targetR
	global circleL
	global circleR
	global rgorb
	global lgorb
	global cpps
	global Rerror
	global Lerror
	global targetnum
	global targettol
	global RHS
	global LHS
	global phase
	global flagRHS
	global flagLHS
	global Ralpha
	global Lalpha
	global Rspeed
	global Lspeed
	global stepind
	global neutralR
	global neutralL
	
	while not endflag.isSet():
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		#look for marker data
		try:
			RANKY = float(data["RANK"][1])/1000
			LANKY = float(data["LANK"][1])/1000
			RHIPY = float(data["RGT"][1])/1000
			LHIPY = float(data["LGT"][1])/1000
			
		except:
			try:
				RHIPY = float(data["RHIP"][1])/1000
				LHIPY = float(data["LHIP"][1])/1000
			except:
				print(["ERROR: incorrect or missing marker data..."])
		
#		print("RANKY",RANKY)

		Ralpha = (RHIPY+LHIPY)/2-RANKY
		Lalpha = (LHIPY+RHIPY)/2-LANKY
		
		
		if (phase == 0): #move the leg furthest away
#				messagewin.setText('Moving...')
#				messagewin.visible(1)
				#move to the initial pose
				
				try:
					if (randy[stepind-1] == 2):#previous test was right leg, move right leg first 
						if (Rz<-30) & (Lz<-30) & (abs(1.45-RANKY) >= 0.04):
							Rspeed = int(300*math.copysign(1,1.45-RANKY))
						elif (abs(1.45-RANKY) < 0.04):
							Rspeed = 0
							phase = 1
#							print('phase',phase)
						else:
							Rspeed = 0
							print('Balance loss detected, stopped')
					elif (randy[stepind-1] == 1):
						if (Rz<-30) & (Lz<-30) & (abs(1.45-LANKY) >= 0.04):
							Lspeed = int(300*math.copysign(1,1.45-LANKY))
						elif (abs(1.45-LANKY) < 0.04):
							Lspeed = 0
							phase = 1
#							print('phase',phase)
						else:
							Lspeed = 0
#							print('Balance loss detected, stopped')
				except:
					disp('Max # of steps reached?')
					Rspeed = 0
					Lspeed = 0

		elif (phase == 1): #move the other leg
#			viz.visible(0)
#			messagewin.setText('Moving...')
			#move to the initial pose
			try:
				if (randy[stepind-1] == 2):#previous test was right leg, move right leg first 
					if (Rz<-30) & (Lz<-30) & (abs(1.45-LANKY) >= 0.04):
						Lspeed = int(300*math.copysign(1,1.45-LANKY))
					else:
						Lspeed = 0
						phase = 2
#						print('phase',phase)
				elif (randy[stepind-1] == 1):
					if (Rz<-30) & (Lz<-30) & (abs(1.45-RANKY) > 0.04):
						Rspeed = int(300*math.copysign(1,1.45-RANKY))
					else:
						Rspeed = 0
						phase = 2
#						print('phase',phase)
			except:
				disp('Max # of steps reached?')
				Rspeed = 0
				Lspeed = 0

		elif (phase == 2):#hide the circles
			circleL.visible(0)
			circleR.visible(0)
			try:
				if (randy[stepind] == 1):#right side next
					neutralR.visible(1)
				else:
					neutralL.visible(1)
					
				phase = 3
			except:
				#out of steps
				phase = 4
			
		elif (phase == 3):#time for an attempt
			messagewin.visible(0)
					
			#gait events
			if (Rz <= -30) & (histzR > -30):#RHS
				Rerror = targetL-Ralpha
				RHS = 1
				flagRHS = 1
				if (Rerror < targettol):
					rgorb = 1
				else:
					rgorb = 0
				nothing = updatetargetdisplay(Ralpha,circleR,2,2)
#				circleR.visible(1)
			else:
				RHS = 0
				
			if (Lz <= -30) & (histzL > -30):#LHS
				Lerror = targetL-Lalpha
				LHS = 1
				flagLHS = 1
				if (Lerror < targettol):
					lgorb = 1
				else:
					lgorb = 0
				targetnum = updatetargetdisplay(Lalpha,circleL,1,1)
#				circleL.visible(1)
#				targetSLOW = Lalpha
			else:
				LHS = 0

			if flagRHS & flagLHS:#signal to start next phase after both HS
				phase = 0
				flagRHS = 0
				flagLHS = 0
				stepind  =stepind+1
				neutralR.visible(0)
				neutralL.visible(0)
		elif (phase == 4):
			messagewin.setText('Test Complete!')
			messagewin.visible(1)
			if (RANKY-LANKY >= 0.04) & (Rz < -30) & (Lz < -30):
				Lspeed = int(300*math.copysign(1,(RANKY-LANKY)))
				Rspeed = 0
			elif (LANKY-RANKY >= 0.04) & (Rz < -30) & (Lz < -30):
				Rspeed = int(300*math.copysign(1,(LANKY-RANKY)))
				Lspeed = 0
			else:
				Rspeed = 0
				Lspeed = 0
		else:
			disp('Warning phase value un-defined')
		
		#send speed update
		speedlist = [Rspeed,Lspeed,1300,1300,0]#the accelerations "1300 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
		qq.put(speedlist)
			
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,Ralpha,Lalpha,Rerror,Lerror,targetnum,]#organize the data to be written to file
		q3.put(savestring)
		
		
		
	#close cpp server
	cpps.kill()
		
		
def ParseRoot(root):#the purpose of this function is to make sure that marker data is used correctly since they can arrive in different order, depending on the order the models are listed in Nexus
	tempdat = root.split(',')
#	print tempdat
	del tempdat[-1]#the last element is a empty string ""
	data = {}#create dictionary
	
	data["FN"] = int(tempdat[0])#frame number
	data["Rz"] = float(tempdat[4])#right forceplate Z component
	data["Lz"] = float(tempdat[2])#left forceplate Z comp.
	data["DeviceCount"] = float(tempdat[5])# #of devices besides forceplates
	for x in range(6,6+2*int(data["DeviceCount"])-1,2):  #assumes one value per device for now...
		temp = tempdat[x]
		data[temp] = [tempdat[x+1]]
#		print temp
	
	#place marker data into dictionary
	for z in range(6+2*int(data["DeviceCount"]),len(tempdat),4):
		temp = tempdat[z]
#		print temp
		data[temp] = [tempdat[z+1],tempdat[z+2],tempdat[z+3]]
		
#	print data
	return data

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
		global FNold
		global repeatcount
		data = s.recv(50)#receive the initial message
#		print(data)
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
			root = databuf
#			print('root',root)
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
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
	mststring = str(mst2)+'EXP2B_DK2_V6.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RGORB','LGORB','Ralpha','Lalpha','Rerror','Lerror','targetnumber'],file)
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
	
endflag = threading.Event()#an event to raise when we are ready to stop recording
def raisestop(sign):
	#the sign passed in doesn't do anything, I just didn't know how to make this work without passing something in...
	print("stop flag raised")
	endflag.set()
#	t1.join(5)
#	t2.join(5)
#	t3.join(5)
#	t4.join(5)
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
	














