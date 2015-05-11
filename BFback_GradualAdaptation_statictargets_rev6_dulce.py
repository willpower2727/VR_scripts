#script runs biofeedback routine with TMM, Vicon. Gives feedback on the length of step 
#while in gait. 

#revision 5 starts to keep track of the last 12 steps' scale factors and a report is given at the end so if the program is restarted you can preserve the last scales used with catchflag
#uses new gorb formula
#3/3/2015

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
import math

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)
time.sleep(2)#show off a litle bit...

#indicate flag for post-catch targets, which last for the first 12 steps
global catchflag
catchflag = 0
global stridecounter
stridecounter = 0

#set target tolerance for stride length
global targetL
targetL = 0.5

global targetR
targetR = 0.5 

global targettol
targettol = 0.025

global targettolD
targettolD = 0.05

global boxL
boxL = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.2,0.005,targettolD*2])
boxL.setPosition([-0.2,targetL,0])
boxL.setEuler(0,90,0)
global boxR
boxR = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.2,0.005,targettolD*2])
boxR.setPosition([0.2,targetR,0])
boxR.setEuler(0,90,0)
viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels to count successful steps taken
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[4.6,3*targetR,12])
rightcounter.visible(0)
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-5.5,3*targetL,12])
leftcounter.visible(0)

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
global histL
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

Ltop = -.3107
Lhsp = 0.2184
Rtop = -0.2999
Rhsp = 0.253

#keep track of each step, whether it is good or bad
global Rgorb
global Lgorb
Rgorb = 0
Lgorb = 0

#R Rigth leg 
global R
R = 1.2
#R left leg
global R2
R2 = 1.2

global rsci
rsci = 2
global lsci
lsci = 2.2

global RHS
RHS = 0
global LHS
LHS = 0

global Rlist
global Llist
Rlist = [0] * 4#list of previous 4 scales
Llist = [0] * 4

global fakeTargetR
global fakeTargetL
fakeTargetR = Rhsp
fakeTargetL = Lhsp


def UpdateViz(root,q,savestring,q3):
	timeold = time.time()

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
		global steplengthL
		global steplengthR
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
		
		cursorR.setScale(0.1,rsci*(RHIPY-RANKY),0.01250)
		cursorL.setScale(-0.1,lsci*(LHIPY-LANKY),0.01250)
		
		#determine if we need to hide the cursor
		if (RHIPY-RANKY < 0) | (Rz < -30):
			cursorR.visible(0)
		else:
			cursorR.visible(1)
		
		if (LHIPY-LANKY < 0) | (Lz < -30):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
			
		#detect gait events
		if (Rz <= -30) & (histzR >-30): #RHS
			HistBallR.setPosition([0.2,rsci*(RHIPY-RANKY), 0])
			steplengthR = rsci*(RHIPY-RANKY)
			stridecounter = stridecounter+1
			RHS = 1
			if (psudoR == 5):
				Rhsp = RHIPY-RANKY#update the alpha value
				rsci = 0.5*(1/(Rhsp+1/(1+R)*(abs(Rtop)-R*Rhsp)))#find new scale factor
				fakeTargetR = abs(Rhsp)+(1/(1+R))*(abs(Rtop)-(R*abs(Rhsp)))#find the theoretical target
				Rlist.append(rsci)#add the scale to the end of the list
				Rlist.pop(0)#remove the oldest one
#				print("rsci is: ")
#				print(rsci)
			if (abs(rsci*(RHIPY-RANKY)-targetR) <= targettol*rsci):
				RCOUNT = RCOUNT+1
				boxR.color( viz.WHITE )
				rightcounter.message(str(RCOUNT))
				Rgorb = 1  #flag this step as good or bad
			else:
				boxR.color( viz.BLUE )
				Rgorb = 0
			if (catchflag == 1) & (stridecounter > 12):
				boxR.setPosition([0.2,targetR,0])
#				continue
			elif (catchflag == 1) & (stridecounter <= 12):
				rsci = 1.587
			else:
#				continue
				boxR.setPosition([0.2,targetR,0])
		elif (Rz >= -30) & (histzR < -30): #RTO
			#calculate Toe-Off position
			if (psudoR == 5):
				Rtop = RHIPY-RANKY#update beta value
				psudoR = 1
			psudoR = psudoR+1
			RHS = 0
		else:
			RHS = 0
#		if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit within tolerance
#			boxR.color( viz.WHITE )
#		else:
#			boxR.color( viz.BLUE )
				
		
		if (Lz <= -30) & (histzL >-30): #LHS
			HistBallL.setPosition([-0.2,lsci*(LHIPY-LANKY), 0])
			steplengthL = lsci*(LHIPY-LANKY)
			stridecounter = stridecounter+1
			LHS = 1
			if (psudoL == 5):
				Lhsp = LHIPY-LANKY#update the alpha value
				lsci = 0.5*(1/(Lhsp+1/(1+R2)*(abs(Ltop)-R2*Lhsp)))
				fakeTargetL = abs(Lhsp)+(1/(1+R2))*(abs(Ltop)-(R2*abs(Lhsp)))
				Llist.append(lsci)
				Llist.pop(0)
#				print("lsci is: ")
#				print(lsci)
			if (abs(lsci*(LHIPY-LANKY)-targetL) <= targettol*lsci):
				LCOUNT = LCOUNT+1
				boxL.color( viz.WHITE )
				leftcounter.message(str(LCOUNT))
				Lgorb = 1  #flag this step as good or bad
			else:
				boxL.color( viz.BLUE )
				Lgorb = 0
			if (catchflag == 1) & (stridecounter > 12):
				boxL.setPosition([-0.2,targetL,0])
#				continue
			elif (catchflag == 1) & (stridecounter <= 12):
				lsci = 2.371
			else:
				boxL.setPosition([-0.2,targetL,0])
#				continue
		elif (Lz >= -30) & (histzL < -30): #LTO
			#calculate Toe-Off position
			if (psudoL == 5):
				Ltop = LHIPY-LANKY#update beta value
				psudoL = 1
			psudoL = psudoL+1
			LHS = 0
		else:
			LHS = 0
#		if (abs(steplengthL-targetL) <= targettol):#highlight the target when the target is hit within tolerance
#			boxL.color( viz.WHITE )
#		else:
#			boxL.color( viz.BLUE )
		
		histzR = Rz
		histzL = Lz

		#send some data to be saved
		fn = root.find(".//FrameNumber")#find the frame number
		fnn = fn.attrib.values()
#		print(fnn[0])
		
		savestring = [int(fnn[0]),Rz,Lz,RHS,LHS,Rgorb,Lgorb,RHIPY-RANKY,LHIPY-LANKY,rsci,lsci,RHIPY,LHIPY,RANKY,LANKY,fakeTargetR,fakeTargetL]#organize the data to be written to file
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
			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
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
	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RGORB','LGORB','Ralpha','Lalpha','Rscale','Lscale','RHIPY','LHIPY','RANKY','LANKY','targetR','targetL'],file)
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
	