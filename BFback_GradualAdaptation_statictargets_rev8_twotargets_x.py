<<<<<<< HEAD
﻿#Gives feedback on the length of step 
#while in gait. 

#revision 8 use    V2P R3
#WDA & DMMO
#4/14/2015

import socket
import sys
import io
import re
#from xml.etree import ElementTree   #old slower method
#import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
import math
import cProfile
import subprocess

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_rev3/x64/Release/Vicon2Python_rev3.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)
time.sleep(2)#show off a litle bit...

viz.startLayer(viz.LINES) 
viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
viz.vertex(1,-0.25,-0.0001) 
myLines = viz.endLayer() 
#indicate flag for post-catch targets, which last for the first 12 steps
global catchflag
catchflag =0
global stridecounter
stridecounter = 0

#set target tolerance for stride length
global targetL
targetL = 0.25
global targetR
targetR = 0.25
global targettol
targettol = 0.025
global targetto2
targetto2 = 0.0375
##################################################################################
global boxR
boxR = viz.addTexQuad(pos=[0.2,0,0.001],scale=[0.2,2*targettol,0])
boxR.color(0,0,1)
boxR.alpha(0.9)
global boxR2
boxR2 = viz.addTexQuad(pos=[0.2,0,0.001],scale=[0.2,2*targetto2,0])
boxR2.color(0.2,0.8,1)
boxR2.alpha(0.9)

global boxL
boxL = viz.addTexQuad(pos=[-0.2,0,0.001],scale=[0.2,2*targettol,0])
boxL.color(0,0,1)
boxL.alpha(0.9)

global boxL2
boxL2 = viz.addTexQuad(pos=[-0.2,0,0.001],scale=[0.2,2*targetto2,0])
boxL2.color(0.2,0.8,1)
boxL2.alpha(0.9)

global distheta#the view angles we'll need later
distheta = 2*math.atan2(2*targettol,2*1)
global widetheta
widetheta = 2*math.atan2(0.2,2*1)

global distZ
distRZ = 2*targettol/(2*math.tan(distheta/2))
global wideX
wideRX = 2*(distRZ)*math.tan(widetheta/2)
print(wideRX)
global distLZ
distLZ = distRZ
global wideLX
wideLX = wideRX

global cursorR
#cursorR = viz.addTexQuad(pos=[0.2,-0.25,0.001],scale=[0.1,0.01,0])
#cursorR.color(viz.RED)
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,-targetR,0])
cursorR.disable(viz.LIGHTING)#we want unrealistic lighting to avoid perspective

global cursorL
#cursorL = viz.addTexQuad(pos=[-0.2,-0.25,0.001],scale=[0.1,0.01,0])
#cursorL.color(viz.GREEN)
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,-targetL,0])
cursorL.disable(viz.LIGHTING)

global HistBallR
HistBallR = viz.add('box.wrl', color=(1,0.6,0), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,0,0])
#HistBallR.alpha(0.8)
#HistBallR.disable(viz.LIGHTING)
#
global HistBallL
HistBallL = viz.add('box.wrl', color=(1,0.6,0), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,0,0])
#HistBallL.alpha(0.8)
#HistBallL.disable(viz.LIGHTING)

viz.MainView.setPosition(0,0,-1)
viz.MainView.setEuler(0,0,0)
###################################################################################
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0

global histzR
histzR = 0
global histL
histzL = 0

global psudoR
global psudoL
	
psudoR = 0
psudoL = 0

global Rtop
global Rhsp
global Ltop
global Lhsp
global xR	
global xL

Ltop = 0
Lhsp = .26021
Rtop = 0
Rhsp = 0.26735
xR=-0.25423
xL=-0.27941

#keep track of each step, whether it is good or bad
global Rgorb
global Lgorb
Rgorb = 0
Lgorb = 0

#R Rigth leg with X 
global R
R = 0.9526
#R left leg with X 
global R2
R2 =1.09

global rsci
rsci =0.9359#1.095
global lsci
lsci =0.96843#0.981

global RHS
RHS = 0
global LHS
LHS = 0
global RTO
RTO = 0
global LTO
LTO = 0

global n
n=1

global Rlist
global Llist
Rlist = [0] * 4#list of previous 4 scales
Llist = [0] * 4

global fakeTargetR
global fakeTargetL
fakeTargetR = 0.25/rsci
fakeTargetL = 0.25/lsci


def UpdateViz(root,q,savestring,q3):
#	timeold = time.time()

	while not endflag.isSet():
		global rsci
		global lsci
		global R
		global R2
		global histzR
		global histzL
		global Rhsp
		global Lhsp
		global Rtop
		global Ltop
		global RCOUNT
		global LCOUNT
		global catchflag
		global Rgorb
		global Lgorb
		global stridecounter
		global psudoL
		global psudoR
		global RHS
		global LHS
		global Rlist
		global Llist
		global fakeTargetR
		global fakeTargetL
		global distheta
		global widetheta
		global distRZ
		global wideRX
		global distLZ
		global wideLX
		global RTO
		global LTO
		global xR
		global xL
		global n
		global cpps
		
		#get some data
		root = q.get()
		tempdat = root.split(',')
		FN = int(tempdat[0])
		Rz = float(tempdat[3])
		Lz = float(tempdat[2])
		RHIPY = float(tempdat[4])/1000
		LHIPY = float(tempdat[5])/1000
		RANKY = float(tempdat[6])/1000
		LANKY = float(tempdat[7])/1000
		#find the data we need from the frame packet
#		lp1 = root.find(".//FP_0/SubF_7/Fz")#Left Treadmill
#		rp1 = root.find(".//FP_1/SubF_7/Fz")#Right Treadmill
#		s0rhipy = root.find(".//Sub0/RHIP/Y")
#		s0lhipy = root.find(".//Sub0/LHIP/Y")
#		s0ranky = root.find(".//Sub0/RANK/Y")
#		s0lanky = root.find(".//Sub0/LANK/Y")

#		temp = rp1.attrib.values()
#		Rz = float(temp[0])#cast forceplate data as float
#		temp1 = lp1.attrib.values()
#		Lz = float(temp1[0])
#		temp2 = s0rhipy.attrib.values()
#		RHIPY = float(temp2[0])/1000 #convert to meters
#		temp3 = s0lhipy.attrib.values()
#		LHIPY = float(temp3[0])/1000
#		temp4 = s0ranky.attrib.values()
#		RANKY = float(temp4[0])/1000
#		temp5 = s0lanky.attrib.values()
#		LANKY = float(temp5[0])/1000
	
		#determine if we need to hide the cursor
		if ((abs(RHIPY+LHIPY)/2)-RANKY < 0) | (Rz < -30):
			cursorR.visible(0)
		else:
			cursorR.visible(1)
		
		if ((abs(RHIPY+LHIPY)/2)-LANKY < 0) | (Lz < -30):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
		
		
		cursorR.setScale(0.1,rsci*((abs(RHIPY+LHIPY)/2)-RANKY),-0.001)
#		print("rsci*(RHIPY-RANKY) is: ",rsci*(RHIPY-RANKY))
		cursorL.setScale(-0.1,lsci*((abs(RHIPY+LHIPY)/2)-LANKY),-0.001)
#		print("lsci*(LHIPY-LANKY) is: ",lsci*(LHIPY-LANKY))
		
		if  (catchflag ==0) | (stridecounter >8):# (stridecounter > 8):
			HistBallL.visible(1)
			HistBallR.visible(1)
			boxL.visible(1)
			boxL2.visible(1)
			boxR.visible(1)
			boxR2.visible(1)
			#detect gait events
			if (Rz <= -30) & (histzR >-30): #RHS
				HistBallR.setPosition([wideRX,rsci*((abs(RHIPY+LHIPY)/2)-RANKY)-0.25,distRZ-1.001])
				HistBallR.setScale(wideRX,rsci*0.01,0.001)
				stridecounter = stridecounter+1
				RHS = 1
				RTO = 0
				Rhsp = (abs(RHIPY+LHIPY)/2)-RANKY#update the alpha value
				xL=(abs(RHIPY+LHIPY)/2)-LANKY #position of left leg at RHS
#				print("Right error is: ",abs(RHIPY-RANKY)-fakeTargetR)
				if (abs((abs(RHIPY+LHIPY)/2)-RANKY-fakeTargetR) <= targetto2):
					RCOUNT = RCOUNT+1
					boxR2.color( viz.WHITE )
					Rgorb = 1  #flag this step as good or bad
					if (abs((abs(RHIPY+LHIPY)/2)-RANKY-fakeTargetR) <= targettol):
					 boxR.color( viz.WHITE )
					else:
					 boxR.color( 0,0,1 )
					
				else:
					boxR.color(0,0,1)
					boxR2.color(.2,.8,1)
					Rgorb = 0
			elif (Rz >= -30) & (histzR < -30): #RTO
				#calculate Toe-Off position
				RTO = 1
				Rtop = (abs(RHIPY+LHIPY)/2)-RANKY#update beta value
				if (psudoR == 5):
					rsci = 0.25*(1/(Rhsp+((n/(1+R))*(abs(xR)-R*Rhsp))))#find new scale factor
					fakeTargetR = Rhsp+(n/(1+R))*(abs(xR)-R*Rhsp)#find the theoretical target
#					print('fakeTargetR is:')
#					print(fakeTargetR)
					Rlist.append(rsci)#add the scale to the end of the list
					Rlist.pop(0)#remove the oldest one
					distRZ = rsci*2*targettol/(2*math.tan(distheta/2))
#					print("distRZ is: ",distRZ)
#					print("wideRX is: ",wideRX)
					wideRX = 2*(distRZ)*math.tan(widetheta/2)
					#change target sizes and such
					boxR.setPosition(wideRX,0,distRZ-1)
					boxR.setScale(wideRX,2*rsci*targettol,0)
					boxR2.setPosition(wideRX,0,distRZ-1)
					boxR2.setScale(wideRX,2*rsci*targetto2,0)
#					HistBallR.setPosition([wideRX,rsci*Rhsp-0.25,distRZ-1.001])
					psudoR = 1
				psudoR = psudoR+1
				RHS = 0
			else:
				RHS = 0
				RTO = 0
			
			if (Lz <= -30) & (histzL >-30): #LHS
				HistBallL.setPosition([-wideLX,lsci*((abs(RHIPY+LHIPY)/2)-LANKY)-0.25,distLZ-1.001])
				HistBallL.setScale(wideLX,lsci*0.01,0.001)
				stridecounter = stridecounter+1
				LHS = 1
				LTO = 0
				Lhsp = (abs(RHIPY+LHIPY)/2)-LANKY#update the alpha value
				xR=(abs(RHIPY+LHIPY)/2)-RANKY #position of right leg at SHS
				if (abs((abs(RHIPY+LHIPY)/2)-LANKY-fakeTargetL) <= targetto2):
					LCOUNT = LCOUNT+1
					boxL2.color( viz.WHITE )
					Lgorb = 1  #flag this step as good or bad
					if (abs((abs(RHIPY+LHIPY)/2)-LANKY-fakeTargetL) <= targettol):
					 boxL.color( viz.WHITE )
					else:
					 boxL.color( 0,0,1)
					
				else:
					boxL.color(0,0,1)
					boxL2.color(0.2,0.8,1)
					Lgorb = 0
			elif (Lz >= -30) & (histzL < -30): #RTO
				#calculate Toe-Off position
				Ltop = (abs(RHIPY+LHIPY)/2)-LANKY#update beta value
				LTO = 1
				LHS = 0
				if (psudoL == 5):
					lsci = 0.25*(1/(Lhsp+((n/(1+R2))*(abs(xL)-R2*Lhsp))))#find new scale factor
					fakeTargetL = Lhsp+(n/(1+R2))*(abs(xL)-R2*Lhsp)#find the theoretical target
#					print('fakeTargetL is:')
#					print(fakeTargetL)
					Llist.append(lsci)#add the scale to the end of the list
					Llist.pop(0)#remove the oldest one
					distLZ = lsci*2*targettol/(2*math.tan(distheta/2))
					wideLX = 2*(distLZ)*math.tan(widetheta/2)
					#change target sizes and such
					boxL.setPosition(-wideLX,0,distLZ-1)
					boxL.setScale(wideLX,2*lsci*targettol,0)
					boxL2.setPosition(-wideLX,0,distLZ-1)
					boxL2.setScale(wideLX,2*lsci*targetto2,0)
#					HistBallL.setPosition([-wideLX,lsci*Lhsp-0.25,distLZ-1.001])
					psudoL = 1
				psudoL = psudoL+1
			else:
				LHS = 0
				LTO = 0
		elif (catchflag == 1) & (stridecounter <=8):
			
			HistBallL.visible(0)
			HistBallR.visible(0)
			cursorL.visible(0)
			cursorR.visible(0)
			boxL.visible(0)
			boxL2.visible(0)
			boxR.visible(0)
			boxR2.visible(0)
#			#detect gait events
			if (Rz <= -30) & (histzR >-30): #RHS
				#HistBallR.setPosition([wideRX,rsci*(RHIPY-RANKY)-0.25,distRZ-1.001])
				#HistBallR.setScale(wideRX,rsci*0.01,0.001)
				stridecounter = stridecounter+1
				RHS = 1
				RTO = 0
				Rhsp = (abs(RHIPY+LHIPY)/2)-RANKY#update the alpha value
				xL= (abs(RHIPY+LHIPY)/2)-LANKY
#				print("Right error is: ",abs(RHIPY-RANKY)-fakeTargetR)
				if (abs((abs(RHIPY+LHIPY)/2)-RANKY-fakeTargetR) <= targetto2):
					RCOUNT = RCOUNT+1
				#	boxR2.color( viz.WHITE )
					Rgorb = 1  #flag this step as good or bad
				#	if (abs(RHIPY-RANKY-fakeTargetR) <= targettol):
				#	 boxR.color( viz.WHITE )
				#	else:
				#	 boxR.color( 0,0,1 )
					
				else:
				#	boxR.color(0,0,1)
				#	boxR2.color(0.2,0.8,1)
					Rgorb = 0
			elif (Rz >= -30) & (histzR < -30): #RTO
				#calculate Toe-Off position
				Rtop = (abs(RHIPY+LHIPY)/2)-RANKY#update beta value
				RTO = 1
				if (psudoR == 5):
					rsci = 0.25*(1/(Rhsp+((n/(1+R))*(abs(xR)-R*Rhsp))))#find new scale factor
					fakeTargetR = abs(Rhsp)+(n/(1+R))*(abs(xR)-(R*Rhsp))#find the theoretical target
#					print('fakeTargetR is:')
#					print(fakeTargetR)
					Rlist.append(rsci)#add the scale to the end of the list
					Rlist.pop(0)#remove the oldest one
					distRZ = rsci*2*targettol/(2*math.tan(distheta/2))
#					print("distRZ is: ",distRZ)
#					print("wideRX is: ",wideRX)
					wideRX = 2*(distRZ)*math.tan(widetheta/2)
					#change target sizes and such
#					boxR.setPosition(wideRX,0,distRZ-1)
#					boxR.setScale(wideRX,2*rsci*targettol,0)
					psudoR = 1
				psudoR = psudoR+1
				RHS = 0
			else:
				RHS = 0
				RTO = 0
			
			if (Lz <= -30) & (histzL >-30): #LHS
				#HistBallL.setPosition([-wideLX,lsci*(LHIPY-LANKY)-0.25,distLZ-1.001])
				#HistBallL.setScale(wideLX,lsci*0.01,0.001)
				stridecounter = stridecounter+1
				LHS = 1
				LTO = 0
				Lhsp = (abs(RHIPY+LHIPY)/2)-LANKY#update the alpha value
				xR= (abs(RHIPY+LHIPY)/2)-RANKY
				if (abs((abs(RHIPY+LHIPY)/2)-LANKY-fakeTargetL) <= targetto2):
					LCOUNT = LCOUNT+1
				#	boxL2.color( viz.WHITE )
					Lgorb = 1  #flag this step as good or bad
				#	if (abs(LHIPY-LANKY-fakeTargetL) <= targettol):
				#	 boxL.color( viz.WHITE )
				#	else:
				
				#	 boxL.color( 0,0,1 )
					
				else:
				#	boxL.color(0,0,1)
				#	boxL2.color(0.2,0.8,1)
					Lgorb = 0
			elif (Lz >= -30) & (histzL < -30): #RTO
				#calculate Toe-Off position
				Ltop = (abs(RHIPY+LHIPY)/2)-LANKY#update beta value
				LTO = 1
				if (psudoL == 5):
					lsci = 0.25*(1/(Lhsp+((n/(1+R2))*(abs(xL)-R2*Lhsp))))#find new scale factor
					fakeTargetL = abs(Lhsp)+(n/(1+R2))*(abs(xL)-(R2*Lhsp))#find the theoretical target
#					print('fakeTargetL is:')
#					print(fakeTargetL)
					Llist.append(lsci)#add the scale to the end of the list
					Llist.pop(0)#remove the oldest one
					distLZ = lsci*2*targettol/(2*math.tan(distheta/2))
					wideLX = 2*(distLZ)*math.tan(widetheta/2)
					#change target sizes and such
#					boxL.setPosition(-wideLX,0,distLZ-1)
#					boxL.setScale(wideLX,2*lsci*targettol,0)
					psudoL = 1
				psudoL = psudoL+1
				LHS = 0
			else:
				LHS = 0
				LTO = 0

		
		histzR = Rz
		histzL = Lz

		#send some data to be saved
#		fn = root.find(".//FN")#find the frame number
#		fnn = fn.attrib.values()
#		print(fnn[0])
		
		savestring = [FN,Rz,Lz,RHS,LHS,RTO,LTO,Rgorb,Lgorb,(abs(RHIPY+LHIPY)/2)-RANKY,(abs(RHIPY-LHIPY)/2)-LANKY,rsci,lsci,(abs(RHIPY+LHIPY)/2),RANKY,LANKY,fakeTargetR,fakeTargetL,xL,xR,((abs(RHIPY+LHIPY)/2)-RANKY)-xL,((abs(RHIPY+LHIPY)/2)-LANKY)-xR ]#organize the data to be written to file
#		print(sys.getsizeof(savestring))
		q3.put(savestring)

#	q3.join()
	cpps.kill()
	print("R scales: ", Rlist)
	print("L scales: ", Llist)
	print("Mean R scales: ", sum(Rlist)/len(Rlist))
	print("Mean L scales: ", sum(Llist)/len(Llist))
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
#			print(sys.getsizeof(databuf))
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			root = databuf
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
	mststring = str(mst2)+'STATTARGsteplength.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RTO','LTO','RGORB','LGORB','Ralpha','Lalpha','Rscale','Lscale','HIPY','RANKY','LANKY','targetR','targetL','xL','xR','steplenghtR','steplenghtL'],file)
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

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
=======
﻿#script runs biofeedback routine with TMM, Vicon. Gives feedback on the length of step 
#while in gait. 

#revision 8 use    V2P R3
#WDA & DMMO
#4/14/2015

import socket
import sys
import io
import re
#from xml.etree import ElementTree   #old slower method
#import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
import math
import cProfile

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)
time.sleep(2)#show off a litle bit...

viz.startLayer(viz.LINES) 
viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
viz.vertex(1,-0.25,-0.0001) 
myLines = viz.endLayer() 
#indicate flag for post-catch targets, which last for the first 12 steps
global catchflag
catchflag =0
global stridecounter
stridecounter = 0

#set target tolerance for stride length
global targetL
targetL = 0.25
global targetR
targetR = 0.25
global targettol
targettol = 0.025
global targetto2
targetto2 = 0.0375
##################################################################################
global boxR
boxR = viz.addTexQuad(pos=[0.2,0,0.001],scale=[0.2,2*targettol,0])
boxR.color(0,0,1)
boxR.alpha(0.9)
global boxR2
boxR2 = viz.addTexQuad(pos=[0.2,0,0.001],scale=[0.2,2*targetto2,0])
boxR2.color(0.2,0.8,1)
boxR2.alpha(0.9)

global boxL
boxL = viz.addTexQuad(pos=[-0.2,0,0.001],scale=[0.2,2*targettol,0])
boxL.color(0,0,1)
boxL.alpha(0.9)

global boxL2
boxL2 = viz.addTexQuad(pos=[-0.2,0,0.001],scale=[0.2,2*targetto2,0])
boxL2.color(0.2,0.8,1)
boxL2.alpha(0.9)

global distheta#the view angles we'll need later
distheta = 2*math.atan2(2*targettol,2*1)
global widetheta
widetheta = 2*math.atan2(0.2,2*1)

global distZ
distRZ = 2*targettol/(2*math.tan(distheta/2))
global wideX
wideRX = 2*(distRZ)*math.tan(widetheta/2)
print(wideRX)
global distLZ
distLZ = distRZ
global wideLX
wideLX = wideRX

global cursorR
#cursorR = viz.addTexQuad(pos=[0.2,-0.25,0.001],scale=[0.1,0.01,0])
#cursorR.color(viz.RED)
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,-targetR,0])
cursorR.disable(viz.LIGHTING)#we want unrealistic lighting to avoid perspective

global cursorL
#cursorL = viz.addTexQuad(pos=[-0.2,-0.25,0.001],scale=[0.1,0.01,0])
#cursorL.color(viz.GREEN)
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,-targetL,0])
cursorL.disable(viz.LIGHTING)

global HistBallR
HistBallR = viz.add('box.wrl', color=(1,0.6,0), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,0,0])
#HistBallR.alpha(0.8)
#HistBallR.disable(viz.LIGHTING)
#
global HistBallL
HistBallL = viz.add('box.wrl', color=(1,0.6,0), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,0,0])
#HistBallL.alpha(0.8)
#HistBallL.disable(viz.LIGHTING)

viz.MainView.setPosition(0,0,-1)
viz.MainView.setEuler(0,0,0)
###################################################################################
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0

global histzR
histzR = 0
global histL
histzL = 0

global psudoR
global psudoL
	
psudoR = 0
psudoL = 0

global Rtop
global Rhsp
global Ltop
global Lhsp
global xR	
global xL

Ltop = 0
Lhsp = .26021
Rtop = 0
Rhsp = 0.26735
xR=-0.25423
xL=-0.27941

#keep track of each step, whether it is good or bad
global Rgorb
global Lgorb
Rgorb = 0
Lgorb = 0

#R Rigth leg with X 
global R
R = 0.9526
#R left leg with X 
global R2
R2 =1.09

global rsci
rsci =0.9359#1.095
global lsci
lsci =0.96843#0.981

global RHS
RHS = 0
global LHS
LHS = 0
global RTO
RTO = 0
global LTO
LTO = 0

global n
n=1

global Rlist
global Llist
Rlist = [0] * 4#list of previous 4 scales
Llist = [0] * 4

global fakeTargetR
global fakeTargetL
fakeTargetR = 0.25/rsci
fakeTargetL = 0.25/lsci


def UpdateViz(root,q,savestring,q3):
#	timeold = time.time()

	while not endflag.isSet():
		global rsci
		global lsci
		global R
		global R2
		global histzR
		global histzL
		global Rhsp
		global Lhsp
		global Rtop
		global Ltop
		global RCOUNT
		global LCOUNT
		global catchflag
		global Rgorb
		global Lgorb
		global stridecounter
		global psudoL
		global psudoR
		global RHS
		global LHS
		global Rlist
		global Llist
		global fakeTargetR
		global fakeTargetL
		global distheta
		global widetheta
		global distRZ
		global wideRX
		global distLZ
		global wideLX
		global RTO
		global LTO
		global xR
		global xL
		global n
		
		#get some data
		root = q.get()
		tempdat = root.split(',')
		FN = int(tempdat[0])
		Rz = float(tempdat[3])
		Lz = float(tempdat[2])
		RHIPY = float(tempdat[4])/1000
		LHIPY = float(tempdat[5])/1000
		RANKY = float(tempdat[6])/1000
		LANKY = float(tempdat[7])/1000
		#find the data we need from the frame packet
#		lp1 = root.find(".//FP_0/SubF_7/Fz")#Left Treadmill
#		rp1 = root.find(".//FP_1/SubF_7/Fz")#Right Treadmill
#		s0rhipy = root.find(".//Sub0/RHIP/Y")
#		s0lhipy = root.find(".//Sub0/LHIP/Y")
#		s0ranky = root.find(".//Sub0/RANK/Y")
#		s0lanky = root.find(".//Sub0/LANK/Y")

#		temp = rp1.attrib.values()
#		Rz = float(temp[0])#cast forceplate data as float
#		temp1 = lp1.attrib.values()
#		Lz = float(temp1[0])
#		temp2 = s0rhipy.attrib.values()
#		RHIPY = float(temp2[0])/1000 #convert to meters
#		temp3 = s0lhipy.attrib.values()
#		LHIPY = float(temp3[0])/1000
#		temp4 = s0ranky.attrib.values()
#		RANKY = float(temp4[0])/1000
#		temp5 = s0lanky.attrib.values()
#		LANKY = float(temp5[0])/1000
	
		#determine if we need to hide the cursor
		if ((abs(RHIPY+LHIPY)/2)-RANKY < 0) | (Rz < -30):
			cursorR.visible(0)
		else:
			cursorR.visible(1)
		
		if ((abs(RHIPY+LHIPY)/2)-LANKY < 0) | (Lz < -30):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
		
		
		cursorR.setScale(0.1,rsci*((abs(RHIPY+LHIPY)/2)-RANKY),-0.001)
#		print("rsci*(RHIPY-RANKY) is: ",rsci*(RHIPY-RANKY))
		cursorL.setScale(-0.1,lsci*((abs(RHIPY+LHIPY)/2)-LANKY),-0.001)
#		print("lsci*(LHIPY-LANKY) is: ",lsci*(LHIPY-LANKY))
		
		if  (catchflag ==0) | (stridecounter >8):# (stridecounter > 8):
			HistBallL.visible(1)
			HistBallR.visible(1)
			boxL.visible(1)
			boxL2.visible(1)
			boxR.visible(1)
			boxR2.visible(1)
			#detect gait events
			if (Rz <= -30) & (histzR >-30): #RHS
				HistBallR.setPosition([wideRX,rsci*((abs(RHIPY+LHIPY)/2)-RANKY)-0.25,distRZ-1.001])
				HistBallR.setScale(wideRX,rsci*0.01,0.001)
				stridecounter = stridecounter+1
				RHS = 1
				RTO = 0
				Rhsp = (abs(RHIPY+LHIPY)/2)-RANKY#update the alpha value
				xL=(abs(RHIPY+LHIPY)/2)-LANKY #position of left leg at RHS
#				print("Right error is: ",abs(RHIPY-RANKY)-fakeTargetR)
				if (abs((abs(RHIPY+LHIPY)/2)-RANKY-fakeTargetR) <= targetto2):
					RCOUNT = RCOUNT+1
					boxR2.color( viz.WHITE )
					Rgorb = 1  #flag this step as good or bad
					if (abs((abs(RHIPY+LHIPY)/2)-RANKY-fakeTargetR) <= targettol):
					 boxR.color( viz.WHITE )
					else:
					 boxR.color( 0,0,1 )
					
				else:
					boxR.color(0,0,1)
					boxR2.color(.2,.8,1)
					Rgorb = 0
			elif (Rz >= -30) & (histzR < -30): #RTO
				#calculate Toe-Off position
				RTO = 1
				Rtop = (abs(RHIPY+LHIPY)/2)-RANKY#update beta value
				if (psudoR == 5):
					rsci = 0.25*(1/(Rhsp+((n/(1+R))*(abs(xR)-R*Rhsp))))#find new scale factor
					fakeTargetR = Rhsp+(n/(1+R))*(abs(xR)-R*Rhsp)#find the theoretical target
#					print('fakeTargetR is:')
#					print(fakeTargetR)
					Rlist.append(rsci)#add the scale to the end of the list
					Rlist.pop(0)#remove the oldest one
					distRZ = rsci*2*targettol/(2*math.tan(distheta/2))
#					print("distRZ is: ",distRZ)
#					print("wideRX is: ",wideRX)
					wideRX = 2*(distRZ)*math.tan(widetheta/2)
					#change target sizes and such
					boxR.setPosition(wideRX,0,distRZ-1)
					boxR.setScale(wideRX,2*rsci*targettol,0)
					boxR2.setPosition(wideRX,0,distRZ-1)
					boxR2.setScale(wideRX,2*rsci*targetto2,0)
#					HistBallR.setPosition([wideRX,rsci*Rhsp-0.25,distRZ-1.001])
					psudoR = 1
				psudoR = psudoR+1
				RHS = 0
			else:
				RHS = 0
				RTO = 0
			
			if (Lz <= -30) & (histzL >-30): #LHS
				HistBallL.setPosition([-wideLX,lsci*((abs(RHIPY+LHIPY)/2)-LANKY)-0.25,distLZ-1.001])
				HistBallL.setScale(wideLX,lsci*0.01,0.001)
				stridecounter = stridecounter+1
				LHS = 1
				LTO = 0
				Lhsp = (abs(RHIPY+LHIPY)/2)-LANKY#update the alpha value
				xR=(abs(RHIPY+LHIPY)/2)-RANKY #position of right leg at SHS
				if (abs((abs(RHIPY+LHIPY)/2)-LANKY-fakeTargetL) <= targetto2):
					LCOUNT = LCOUNT+1
					boxL2.color( viz.WHITE )
					Lgorb = 1  #flag this step as good or bad
					if (abs((abs(RHIPY+LHIPY)/2)-LANKY-fakeTargetL) <= targettol):
					 boxL.color( viz.WHITE )
					else:
					 boxL.color( 0,0,1)
					
				else:
					boxL.color(0,0,1)
					boxL2.color(0.2,0.8,1)
					Lgorb = 0
			elif (Lz >= -30) & (histzL < -30): #RTO
				#calculate Toe-Off position
				Ltop = (abs(RHIPY+LHIPY)/2)-LANKY#update beta value
				LTO = 1
				LHS = 0
				if (psudoL == 5):
					lsci = 0.25*(1/(Lhsp+((n/(1+R2))*(abs(xL)-R2*Lhsp))))#find new scale factor
					fakeTargetL = Lhsp+(n/(1+R2))*(abs(xL)-R2*Lhsp)#find the theoretical target
#					print('fakeTargetL is:')
#					print(fakeTargetL)
					Llist.append(lsci)#add the scale to the end of the list
					Llist.pop(0)#remove the oldest one
					distLZ = lsci*2*targettol/(2*math.tan(distheta/2))
					wideLX = 2*(distLZ)*math.tan(widetheta/2)
					#change target sizes and such
					boxL.setPosition(-wideLX,0,distLZ-1)
					boxL.setScale(wideLX,2*lsci*targettol,0)
					boxL2.setPosition(-wideLX,0,distLZ-1)
					boxL2.setScale(wideLX,2*lsci*targetto2,0)
#					HistBallL.setPosition([-wideLX,lsci*Lhsp-0.25,distLZ-1.001])
					psudoL = 1
				psudoL = psudoL+1
			else:
				LHS = 0
				LTO = 0
		elif (catchflag == 1) & (stridecounter <=8):
			
			HistBallL.visible(0)
			HistBallR.visible(0)
			cursorL.visible(0)
			cursorR.visible(0)
			boxL.visible(0)
			boxL2.visible(0)
			boxR.visible(0)
			boxR2.visible(0)
#			#detect gait events
			if (Rz <= -30) & (histzR >-30): #RHS
				#HistBallR.setPosition([wideRX,rsci*(RHIPY-RANKY)-0.25,distRZ-1.001])
				#HistBallR.setScale(wideRX,rsci*0.01,0.001)
				stridecounter = stridecounter+1
				RHS = 1
				RTO = 0
				Rhsp = (abs(RHIPY+LHIPY)/2)-RANKY#update the alpha value
				xL= (abs(RHIPY+LHIPY)/2)-LANKY
#				print("Right error is: ",abs(RHIPY-RANKY)-fakeTargetR)
				if (abs((abs(RHIPY+LHIPY)/2)-RANKY-fakeTargetR) <= targetto2):
					RCOUNT = RCOUNT+1
				#	boxR2.color( viz.WHITE )
					Rgorb = 1  #flag this step as good or bad
				#	if (abs(RHIPY-RANKY-fakeTargetR) <= targettol):
				#	 boxR.color( viz.WHITE )
				#	else:
				#	 boxR.color( 0,0,1 )
					
				else:
				#	boxR.color(0,0,1)
				#	boxR2.color(0.2,0.8,1)
					Rgorb = 0
			elif (Rz >= -30) & (histzR < -30): #RTO
				#calculate Toe-Off position
				Rtop = (abs(RHIPY+LHIPY)/2)-RANKY#update beta value
				RTO = 1
				if (psudoR == 5):
					rsci = 0.25*(1/(Rhsp+((n/(1+R))*(abs(xR)-R*Rhsp))))#find new scale factor
					fakeTargetR = abs(Rhsp)+(n/(1+R))*(abs(xR)-(R*Rhsp))#find the theoretical target
#					print('fakeTargetR is:')
#					print(fakeTargetR)
					Rlist.append(rsci)#add the scale to the end of the list
					Rlist.pop(0)#remove the oldest one
					distRZ = rsci*2*targettol/(2*math.tan(distheta/2))
#					print("distRZ is: ",distRZ)
#					print("wideRX is: ",wideRX)
					wideRX = 2*(distRZ)*math.tan(widetheta/2)
					#change target sizes and such
#					boxR.setPosition(wideRX,0,distRZ-1)
#					boxR.setScale(wideRX,2*rsci*targettol,0)
					psudoR = 1
				psudoR = psudoR+1
				RHS = 0
			else:
				RHS = 0
				RTO = 0
			
			if (Lz <= -30) & (histzL >-30): #LHS
				#HistBallL.setPosition([-wideLX,lsci*(LHIPY-LANKY)-0.25,distLZ-1.001])
				#HistBallL.setScale(wideLX,lsci*0.01,0.001)
				stridecounter = stridecounter+1
				LHS = 1
				LTO = 0
				Lhsp = (abs(RHIPY+LHIPY)/2)-LANKY#update the alpha value
				xR= (abs(RHIPY+LHIPY)/2)-RANKY
				if (abs((abs(RHIPY+LHIPY)/2)-LANKY-fakeTargetL) <= targetto2):
					LCOUNT = LCOUNT+1
				#	boxL2.color( viz.WHITE )
					Lgorb = 1  #flag this step as good or bad
				#	if (abs(LHIPY-LANKY-fakeTargetL) <= targettol):
				#	 boxL.color( viz.WHITE )
				#	else:
				
				#	 boxL.color( 0,0,1 )
					
				else:
				#	boxL.color(0,0,1)
				#	boxL2.color(0.2,0.8,1)
					Lgorb = 0
			elif (Lz >= -30) & (histzL < -30): #RTO
				#calculate Toe-Off position
				Ltop = (abs(RHIPY+LHIPY)/2)-LANKY#update beta value
				LTO = 1
				if (psudoL == 5):
					lsci = 0.25*(1/(Lhsp+((n/(1+R2))*(abs(xL)-R2*Lhsp))))#find new scale factor
					fakeTargetL = abs(Lhsp)+(n/(1+R2))*(abs(xL)-(R2*Lhsp))#find the theoretical target
#					print('fakeTargetL is:')
#					print(fakeTargetL)
					Llist.append(lsci)#add the scale to the end of the list
					Llist.pop(0)#remove the oldest one
					distLZ = lsci*2*targettol/(2*math.tan(distheta/2))
					wideLX = 2*(distLZ)*math.tan(widetheta/2)
					#change target sizes and such
#					boxL.setPosition(-wideLX,0,distLZ-1)
#					boxL.setScale(wideLX,2*lsci*targettol,0)
					psudoL = 1
				psudoL = psudoL+1
				LHS = 0
			else:
				LHS = 0
				LTO = 0

		
		histzR = Rz
		histzL = Lz

		#send some data to be saved
#		fn = root.find(".//FN")#find the frame number
#		fnn = fn.attrib.values()
#		print(fnn[0])
		
		savestring = [FN,Rz,Lz,RHS,LHS,RTO,LTO,Rgorb,Lgorb,(abs(RHIPY+LHIPY)/2)-RANKY,(abs(RHIPY-LHIPY)/2)-LANKY,rsci,lsci,(abs(RHIPY+LHIPY)/2),RANKY,LANKY,fakeTargetR,fakeTargetL,xL,xR,((abs(RHIPY+LHIPY)/2)-RANKY)-xL,((abs(RHIPY+LHIPY)/2)-LANKY)-xR ]#organize the data to be written to file
#		print(sys.getsizeof(savestring))
		q3.put(savestring)

#	q3.join()
	print("R scales: ", Rlist)
	print("L scales: ", Llist)
	print("Mean R scales: ", sum(Rlist)/len(Rlist))
	print("Mean L scales: ", sum(Llist)/len(Llist))
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
#			print(sys.getsizeof(databuf))
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			root = databuf
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
	mststring = str(mst2)+'STATTARGsteplength.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RTO','LTO','RGORB','LGORB','Ralpha','Lalpha','Rscale','Lscale','HIPY','RANKY','LANKY','targetR','targetL','xL','xR','steplenghtR','steplenghtL'],file)
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

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
>>>>>>> origin/master
	