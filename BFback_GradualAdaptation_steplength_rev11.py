#script runs biofeedback routine with python c++ server
#
#targets of alpha distance are updated every few strides to match subject behavior during gradual split
#This is for awareness of adaptation
# V2P PyAd
#revision 11    1/24/2017   WDA, adds latest saving methods and exploding targets, updated look too

import socket
import sys
import io
import re
import viz
import threading
import Queue
import time
import csv
import vizact
import math
import subprocess

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/PyAdaptVicon2Python/x64/Release/PyAdaptVicon2Python.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN #run world in full screen
)
time.sleep(1)
#indicate flag for post-catch targets, which last for the first 12 steps
global catchflag
catchflag = 0
global stridecounter
stridecounter = 0

#set target alpha values
global targetL
targetL = 0.186
global targetR
targetR = 0.205

global scaling
scaling = 1

#R Rigth leg 
global R
R = 1.54
#R left leg
global R2
R2 = 1.73

global targettol
#targettol = 0.025
targettol = 0.0375

global boxL
boxL = viz.addTexQuad(pos=[-0.2,targetL,0],scale=[0.2,2*targettol,0])
boxL.color(0,0.7,1)
boxL.alpha(0.7)
global boxR
boxR = viz.addTexQuad(pos=[0.2,targetR,0],scale=[0.2,2*targettol,0])
boxR.color(0,0.7,1)
boxR.alpha(0.7)

viz.MainView.setPosition(0, 0.25, -1.25)
viz.MainView.setEuler(0,0,0)

#setup explosions
global fire1
fire1 = viz.addChild('fire2.osg',scale=[2,2,2],pos=[0.2,targetR,0]) #right side
global fire2
fire2 = viz.addChild('fire2.osg',scale=[2,2,2],pos=[-0.2,targetL,0]) #left side
fire1.setEuler(0,90,0)
fire1.visible(0)
fire2.setEuler(0,90,0)
fire2.visible(0)
viz.phys.enable()
viz.phys.setGravity(0,0,0)

global rxplode
rxplode = viz.addChild('ExT1.osgb',pos=[0.2,targetR+targettol,0.005],scale=[2*targettol,2*targettol,0.00125])#make the target explode

global lxplode
lxplode = viz.addChild('ExT1.osgb',pos=[-0.2,targetL+targettol,0.005],scale=[2*targettol,2*targettol,0.00125])

def hide1(nothing):
	global fire1
	global boxR
	global HistBallR
	boxR.color(0,0.7,1)
	fire1.visible(0)
	boxR.visible(1)
	HistBallR.visible(1)

def hide2(nothing):
	global fire2
	global boxL
	global HistBallL
	boxL.color(0,0.7,1)
	fire2.visible(0)
	boxL.visible(1)
	HistBallL.visible(1)

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
#cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorR = viz.add('box3.obj', scale=[0.2,0.1,0.001], cache=viz.CACHE_NONE)
#cursorR.setPosition([0.2,-1*faketarget,0])
cursorR.color(0.5,0.5,0.5)
cursorR.setPosition([0.2,0,0])
cursorR.disable(viz.LIGHTING)#we want unrealistic lighting to avoid perspective

global cursorL
#cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorL = viz.add('box3.obj', scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
cursorL.color(0.5,0.5,0.5)
#cursorL.setPosition([-0.2,-1*faketarget,0])
cursorL.setPosition([-0.2,0,0])
cursorL.disable(viz.LIGHTING)

global HistBallR
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.2,0.01,0.0125], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR*scaling,0])
HistBallR.alpha(0.8)

global histzR
histzR = 0
global histzL
histzL = 0

global HistBallL
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.2,0.01,0.0125], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL*scaling,0])
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

global RTO
global LTO
RTO = 0
LTO = 0

global FNold
FNold = 0
global repeatcount
repeatcount = 0

global Rlist
global Llist
Rlist = [0] * 4
Llist = [0] * 4

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
		global RTO
		global LTO
		global Rlist
		global Llist
		global scaling
		global cpps
		
		#get some data
		root = q.get()
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		try:
			RHIPY = float(data["RGT"][1])/1000
			LHIPY = float(data["LGT"][1])/1000
		except:
			RHIPY = float(data["RHIP"][1])/1000
			LHIPY = float(data["LHIP"][1])/1000
		RANKY = float(data["RANK"][1])/1000
		LANKY = float(data["LANK"][1])/1000

		cursorR.setScale(0.1,((abs(RHIPY+LHIPY)/2)-RANKY),0.01250) #alpha
		cursorL.setScale(-0.1,((abs(RHIPY+LHIPY)/2)-LANKY),0.01250)
		
		#determine if we need to hide the cursor
		if ((abs(RHIPY+LHIPY)/2)-RANKY < 0) | (Rz < -30):
			cursorR.visible(0)
		else:
			cursorR.visible(1)
		if ((abs(RHIPY+LHIPY)/2)-LANKY < 0) | (Lz < -30):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
		
		if (catchflag == 0) | (stridecounter > 12):
			if (Rz <= -30) & (histzR > -30): #RHS condition
				HistBallR.setPosition([0.2,((abs(RHIPY+LHIPY)/2)-RANKY), 0])#update yellow history ball when HS happens
				steplengthR = (abs(RHIPY+LHIPY)/2)-RANKY
				stridecounter = stridecounter+1  #this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
				Rhsp = (abs(RHIPY+LHIPY)/2)-RANKY
				psudoR = psudoR +1
				RHS = 1
				RTO = 0
				#if successful step was taken, keep track of it
				if (abs(steplengthR-targetR) <= targettol):
					RCOUNT = RCOUNT+1
					rightcounter.message(str(RCOUNT))
					Rgorb = 1  #flag this step as good or bad
#					boxR.color( viz.WHITE )
					boxR.visible(0)
					HistBallR.visible(0)
					if (abs(steplengthR-targetR)<(targettol/3)):	
						fire1.visible(1)
					rxplode.visible(1)
					rxplode.setAnimationTime(0.1)
					rxplode.setAnimationState(0)
					vizact.ontimer2(0.6,0,hide1,0)
				else:
					Rgorb = 0
					boxR.color(1,0.2,0)
#					boxR.color( viz.BLUE )
			elif (Rz >= -30) & (histzR < -30):#RTO
				#calculate Toe-Off position
				Rtop = (abs(RHIPY+LHIPY)/2)-RANKY
				RHS = 0
				RTO = 1
				if (psudoR >= 5): #if it's time to update target value
	#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
					targetR = abs(Rhsp)+(1/(1+R))*(abs(Rtop)-(R*Rhsp))
					Rlist.append(targetR)
					Rlist.pop(0)
					print('targetR')
					print(targetR)
					psudoR = 1
					boxR.setPosition([0.2,targetR,0])
			else:
				RHS = 0
				RTO = 0
				
			if (Lz <= -30) & (histzL > -30): #LHS condition
				HistBallL.setPosition([-0.2,((abs(RHIPY+LHIPY)/2)-LANKY), 0])#update yellow history ball when HS happens
				steplengthL = (abs(RHIPY+LHIPY)/2)-LANKY
				stridecounter = stridecounter+1#this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
				Lhsp = (abs(RHIPY+LHIPY)/2)-LANKY
				psudoL = psudoL +1
				LHS = 1
				LTO = 0
				#if successful step was taken, keep track of it
				if (abs(steplengthL-targetL) <= targettol):
					LCOUNT = LCOUNT+1
					leftcounter.message(str(LCOUNT))
					Lgorb = 1  #flag this step as good or bad
#					boxL.color( viz.WHITE )
					boxL.visible(0)
					HistBallL.visible(0)
					if (abs(steplengthL-targetL)<(targettol/3)):	
						fire2.visible(1)
					lxplode.visible(1)
					lxplode.setAnimationTime(0.1)
					lxplode.setAnimationState(0)
					vizact.ontimer2(0.6,0,hide2,0)
				else:
					boxL.color(1,0.2,0)
					Lgorb = 0
			elif (Lz >= -30) & (histzL < -30):#LTO
				#calculate Toe-Off position
				Ltop = (abs(RHIPY+LHIPY)/2)-LANKY
				LHS = 0
				LTO = 1
				if (psudoL >= 5): #if it's time to update target value
	#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
					targetL = abs(Lhsp)+(1/(1+R2))*(abs(Ltop)-(R2*Lhsp))
					Llist.append(targetL)
					Llist.pop(0)
					print('targetL')
					print(targetL)
					psudoL = 1
					boxL.setPosition([-0.2,targetL,0])
			else:
				LHS = 0
				LTO = 0
			
		elif (catchflag == 1) & (stridecounter <=12):
			if (Rz <= -30) & (histzR > -30): #RHS condition
				HistBallR.setPosition([0.2,-1*((abs(RHIPY+LHIPY)/2)-RANKY)*scaling, 0])#update yellow history ball when HS happens
				steplengthR = (abs(RHIPY+LHIPY)/2)-RANKY
				stridecounter = stridecounter+1  #this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
				Rhsp = (abs(RHIPY+LHIPY)/2)-RANKY
				psudoR = psudoR +1
				RHS = 1
				RTO = 0
				#if successful step was taken, keep track of it
				if (abs(steplengthR-targetR) <= targettol):
					RCOUNT = RCOUNT+1
					rightcounter.message(str(RCOUNT))
					Rgorb = 1  #flag this step as good or bad
					boxR.visible(0)
					HistBallR.visible(0)
					if (abs(steplengthR-targetR)<(targettol/3)):	
						fire1.visible(1)
					rxplode.visible(1)
					rxplode.setAnimationTime(0.1)
					rxplode.setAnimationState(0)
					vizact.ontimer2(0.6,0,hide1,0)
				else:
					Rgorb = 0
					boxR.color(1,0.2,0)
#					boxR.color( viz.BLUE )
			elif (Rz >= -30) & (histzR < -30):#RTO
				#calculate Toe-Off position
				Rtop = (abs(RHIPY+LHIPY)/2)-RANKY
				RHS = 0
				RTO = 1
				if (psudoR >= 5): #if it's time to update target value
	#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
#					targetR = abs(Rhsp)+(1/(1+R))*(abs(Rtop)-(R*abs(Rhsp)))
					Rlist.append(targetR)
					Rlist.pop(0)
					print('targetR')
					print(targetR)
					psudoR = 1
					boxR.setPosition([0.2,targetR,0])#targetR doesn't change immediately with catchflag on
			else:
				RHS = 0
				RTO = 0
			
			if (Lz <= -30) & (histzL > -30): #LHS condition
				HistBallL.setPosition([-0.2,((abs(RHIPY+LHIPY)/2)-LANKY), 0])#update yellow history ball when HS happens
				steplengthL = (abs(RHIPY+LHIPY)/2)-LANKY
				stridecounter = stridecounter+1#this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
				Lhsp = (abs(RHIPY+LHIPY)/2)-LANKY
				psudoL = psudoL +1
				LHS = 1
				LTO = 0
				#if successful step was taken, keep track of it
				if (abs(steplengthL-targetL) <= targettol):
					LCOUNT = LCOUNT+1
					leftcounter.message(str(LCOUNT))
					Lgorb = 1  #flag this step as good or bad
					boxL.visible(0)
					HistBallL.visible(0)
					if (abs(steplengthL-targetL)<(targettol/3)):	
						fire2.visible(1)
					lxplode.visible(1)
					lxplode.setAnimationTime(0.1)
					lxplode.setAnimationState(0)
					vizact.ontimer2(0.6,0,hide2,0)
				else:
					Lgorb = 0
					boxL.color(1,0.2,0)
#					boxL.color( viz.BLUE )
			elif (Lz >= -30) & (histzL < -30):#LTO
				#calculate Toe-Off position (X)
#				Ltop = LHIPY-LANKY
				Ltop = (abs(RHIPY+LHIPY)/2)-LANKY
				LHS = 0
				LTO = 1
				if (psudoL >= 5): #if it's time to update target value
	#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
#					targetL = abs(Lhsp)+(1/(1+R2))*(abs(Ltop)-(R2*abs(Lhsp)))
					Llist.append(targetL)
					Llist.pop(0)
					print('targetL')
					print(targetL)
					psudoL = 1
					boxL.setPosition([-0.2,targetL,0])
			else:
				LHS = 0
				LTO = 0
		
		histzR = Rz
		histzL = Lz

		savestring = [FN,Rz,Lz,RHS,LHS,RTO,LTO,Rgorb,Lgorb,(abs(RHIPY+LHIPY)/2)-RANKY,(abs(RHIPY+LHIPY)/2)-LANKY,targetR,targetL,(abs(RHIPY+LHIPY)/2),RANKY,LANKY]#organize the data to be written to file
		q3.put(savestring)

#	q3.join()
	cpps.kill()
	print('R targets: ',Rlist)
	print('L targets: ',Llist)
	print('Mean R targets: ',sum(Rlist)/len(Rlist))
	print('Mean L targets: ',sum(Llist)/len(Llist))
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
			root = databuf
#			print(sys.getsizeof(databuf))
#			print(databuf)
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
#			root = xml.etree.cElementTree(xml.etree.ElementTree.fromstring(databuf))
#			fn = root.find(".//FN")#find the frame number
#			fnn = fn.attrib.values()
#			FN = int(fnn[0])
#			if (FN == int(FNold)) & (repeatcount > 30):
#				print("Repeated Frames more than 30 times")
##				break
#			elif (FN == FNold):
#				repeatcount = repeatcount+1
##				print("Repeat count is: ",repeatcount)
#			else:
#				repeatcount = 0
#			FNold = FN
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
	mststring = str(mst2)+'BFback_GA_steplength_dyntargets_rev11.txt'
	print("Data file created named:")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','RTO','LTO','RGORB','LGORB','Ralpha','Lalpha','R target','L target','HIPY','RANKY','LANKY'])
	file.close()
	
	file = open(mststring,'a')#reopen for appending only
	csvw = csv.writer(file)
	while not endflag.isSet():
		savestring = q3.get()#look in the queue for data to write
	
		if savestring is None:
			continue
		else:
			csvw.writerow(savestring)
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
			csvw.writerow(savestring)
			print("data still writing to file")
		
	print("savedata finished writing")
	file.close()
	
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
		
#	print(data)
	return data
	
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

def testex(nothing):
	global rxplode
	global lxplode
	fire1.visible(1)
	fire2.visible(1)
	rxplode.visible(1)
	rxplode.setAnimationTime(0.1)
	rxplode.setAnimationState(0)
	vizact.ontimer2(0.6,0,hide1,0)
	lxplode.visible(1)
	lxplode.setAnimationTime(0.1)
	lxplode.setAnimationState(0)
	vizact.ontimer2(0.6,0,hide2,0)

print("\n")
print("press 'q' to stop")
print("\n")
vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
vizact.onkeydown('s',testex,'biggle')