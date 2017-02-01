<<<<<<< HEAD
﻿#Exp2B
#Alteration of Vazquex Experiment 2B
#
#Subjects walk at a set speed while they try to match (HIP-ANK distance) 
#targets are displayed on a latitudinal grid, 20 targets,
#
#The target is determined based on TM baseline walking
#
#V75 is for post adaptation, instead of displaying feedback of the actual movement, it employs an error clamp (25% of true error)
#REV 3 starts HIP-ANk distance instead of step length
#
#V2P_DK2_R1
#
#William Anderton 5/13/2016

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
#import json
import csv
import vizact
import struct
import array
import math
import subprocess
import win32gui
import numpy as np
import oculus
import vizlens
import os.path

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.go(
#viz.FULLSCREEN #run world in full screen
)

#def file_len(fname):#how many lines are in the error clamp file?
#	for i, l in enumerate(f):
#		pass
#	return i + 1
	

#look for the file
#if os.path.isfile('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\ErrorClamps.csv'):
#	f = open('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\ErrorClamps.csv','r')
#	numline = file_len(f)
#	global Rclamp
#	Rclamp = [0]*numline
#	global Lclamp
#	Lclamp = [0]*numline
#	
#	f.close()
#	f = open('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\ErrorClamps.csv','r')
#	print('numline: ',numline)
#	for z in range(0,numline,1):
#		line = f.readline()
#		line = line.replace('\n','')
#		line2 = line.split(',')
#		Rclamp[z] = float(line2[0])
#		Lclamp[z] = float(line2[1])
#	f.close()
#else:
#	print('ERROR: Error clamp definition file not available, cannot determine error clamps...\n')
	
#print(Rclamp)

#viz.fov(110)
#pincushion = vizlens.PincushionDistortion()
#pincushion.setK1(0.2)

global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor

global targetL
targetL = 0.2311292

global targetR
targetR = 0.2271392

global targetmean
targetmean = (targetR+targetL)/2

global targettol
targettol = 0.02

global circleL #slow leg circle marker
circleL = vizshape.addSphere(0.01,50,50,color=viz.GREEN)
circleL.setPosition(-0.03,targetL,0)
circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global circleR #slow leg circle marker
circleR = vizshape.addSphere(0.01,50,50)
circleR.color(1,0.7,0)
circleR.setPosition(0.04,targetR,0)
circleR.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global highlightr
highlightr = vizshape.addBox(size=[0.25,0.0175,0.001])
highlightr.color(0,0,1)
highlightr.setPosition(0.145,targetmean,0)
highlightr.disable(viz.LIGHTING)

global highlightl
highlightl = vizshape.addBox(size=[0.25,0.0175,0.001])
highlightl.color(0,0,1)
highlightl.setPosition(-0.135,targetmean,0)
highlightl.disable(viz.LIGHTING)

#setup order of highlights
short = -0.2*targetmean
long = 0.2*targetmean
med = 0
global frodo
shortFirst=1;
if (shortFirst == 1):
	frodo = [short]*10
	frodo = frodo + [med]*15
	frodo = frodo + [short]*15
	frodo = frodo + [med]*15
	frodo = frodo + [short]*25
	frodo = frodo + [med]*25
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [med]*50
elif (shortFirst == 0):
	frodo = [med]*10
	frodo = frodo + [short]*15
	frodo = frodo + [med]*15
	frodo = frodo + [short]*15
	frodo = frodo + [med]*25
	frodo = frodo + [short]*25
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
else:
	print('WARNING cannot determine first set please review...')

print(frodo)
global stepind
stepind = 0

highlightr.setPosition(0.145,targetmean+frodo[stepind],0)
highlightl.setPosition(-0.135,targetmean+frodo[stepind],0)

global Rclamp
Rclamp = 0

global Lclamp
Lclamp = 0

global randyclamps
randyclamps = (-0.04,-0.035,-0.03,-0.025,-0.02,-0.015,-0.01,-0.005,0,0.005,0.01,0.015,0.02,0.025,0.03,0.035,0.04)
#print(frodo)
#fakebox = vizshape.addBox(size=[1,0.01,0.001])
#fakebox.setPosition(0,targetmean,0)
#fakebox.color(0,1,0)
#fakebox.disable(viz.LIGHTING)

#create latitudinal grid, "10" is the target step length, the grid expands above and belo
lines = {}#create empty dictionary
for x in range(1,12,1):
	lines["Tp{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
	lines["Tp{0}".format(x)].setPosition(0,targetmean+0.05*targetmean+(x-1)*0.1*targetmean,0)#each gap represents 20 percent of target?
	lines["Tn{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
	lines["Tn{0}".format(x)].setPosition(0,targetmean+0.05*targetmean-(x-1)*0.1*targetmean,0)
#	print((x-1)*0.02)
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,targetmean-0.95*targetmean-0.1*targetmean+x*0.1*targetmean+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,targetmean-0.95*targetmean-0.1*targetmean+x*0.1*targetmean+0.005,0],scale=[0.015,0.015,0.015])
	
viz.MainView.setPosition(0,targetmean+0.05*targetmean, -0.57)
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
	global highlightl
	global highlightr
	global frodo
	global stepind
	global Rclamp
	global Lclamp
	global randyclamps
	
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
				RANKY = float(data["RANK"][1])/1000
				LANKY = float(data["LANK"][1])/1000
				RHIPY = float(data["RHIP"][1])/1000
				LHIPY = float(data["LHIP"][1])/1000
			except:
#				pass
				print(["ERROR: incorrect or missing marker data..."])

		
#		Rgamma = LANKY-RANKY
#		Lgamma = RANKY-LANKY
		
		Ralpha = (RHIPY+LHIPY)/2-RANKY
		Lalpha = (RHIPY+LHIPY)/2-LANKY
		
		#gait events
		if (Rz <= -30) & (histzR > -30):#RHS
			Rerror = Ralpha-(targetmean+frodo[stepind])
			RHS = 1
#			circleR.setPosition(0.05,targetmean+frodo[stepind]+random.choice(randyclamps),0)
#			circleR.setPosition(0.05,targetmean+frodo[stepind]+Rclamp[stepind],0)
			circleR.setPosition(0.05,targetmean+frodo[stepind]+0.35*Rerror,0)
			Rclamp = targetmean+frodo[stepind]+0.35*Rerror
			stepind = stepind+1
#			if (stepind > len(Rclamp)):
			if (stepind > 455):
				print('Task Complete! Out of steps')
			else:
				highlightr.setPosition(0.145,targetmean+frodo[stepind],0)
				highlightl.setPosition(-0.135,targetmean+frodo[stepind],0)
				
			if (Rerror < targettol):
				rgorb = 1
			else:
				rgorb = 0
#			nothing = updatetargetdisplay(Rgamma,circleR,2)
#		elif (Rz >-30) & (histzR<=-30): #RTO
#			highlightr.setPosition(0.145,targetmean+frodo(stepind),0)
		else:
			RHS = 0
			
		if (Lz <= -30) & (histzL > -30):#LHS
			Lerror = Lalpha-(targetmean+frodo[stepind])
			LHS = 1
#			if (stepind > len(Rclamp)):
			if (stepind > 455):
				print('Task Complete! Out of steps')
			else:
#				circleL.setPosition(-0.05,targetmean+frodo[stepind]+random.choice(randyclamps),0)
#				circleL.setPosition(-0.05,targetmean+frodo[stepind]+Lclamp[stepind],0)
				circleL.setPosition(-0.05,targetmean+frodo[stepind]+0.35*Lerror,0)
				Lclamp = targetmean+frodo[stepind]+0.35*Lerror

			if (Lerror < targettol):
				lgorb = 1
			else:
				lgorb = 0
#			targetnum = updatetargetdisplay(Lgamma,circleL,1)
		else:
			LHS = 0

		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,RANKY,LANKY,RHIPY,LHIPY,rgorb,lgorb,Ralpha,Lalpha,Rerror,Lerror,targetmean+frodo[stepind],Rclamp,Lclamp,]#organize the data to be written to file
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
#	print(data["DeviceCount"])
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
	mststring = str(mst2)+'EXP2B_V75_rev3_DK2.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','RANKY','LANKY','RHIPY','LHIPY','RGORB','LGORB','Ralpha','Lalpha','Rerror','Lerror','target','Rclamp','Lclamp'])
#	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RANKY','LANKY','RGORB','LGORB','Rgamma','Lgamma','Rerror','Lerror','target','Rclamp','Lclamp'],file)
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
#t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
#t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
#t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	














=======
﻿#Exp2B
#Alteration of Vazquex Experiment 2B
#
#Subjects walk at a set speed while they try to match (HIP-ANK distance) 
#targets are displayed on a latitudinal grid, 20 targets,
#
#The target is determined based on TM baseline walking
#
#V75 is for post adaptation, instead of displaying feedback of the actual movement, it employs an error clamp (25% of true error)
#REV 3 starts HIP-ANk distance instead of step length
#
#V2P_DK2_R1
#
#William Anderton 5/13/2016

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
#import json
import csv
import vizact
import struct
import array
import math
import subprocess
import win32gui
import numpy as np
import oculus
import vizlens
import os.path

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.go(
#viz.FULLSCREEN #run world in full screen
)

#def file_len(fname):#how many lines are in the error clamp file?
#	for i, l in enumerate(f):
#		pass
#	return i + 1
	

#look for the file
#if os.path.isfile('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\ErrorClamps.csv'):
#	f = open('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\ErrorClamps.csv','r')
#	numline = file_len(f)
#	global Rclamp
#	Rclamp = [0]*numline
#	global Lclamp
#	Lclamp = [0]*numline
#	
#	f.close()
#	f = open('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\ErrorClamps.csv','r')
#	print('numline: ',numline)
#	for z in range(0,numline,1):
#		line = f.readline()
#		line = line.replace('\n','')
#		line2 = line.split(',')
#		Rclamp[z] = float(line2[0])
#		Lclamp[z] = float(line2[1])
#	f.close()
#else:
#	print('ERROR: Error clamp definition file not available, cannot determine error clamps...\n')
	
#print(Rclamp)

#viz.fov(110)
#pincushion = vizlens.PincushionDistortion()
#pincushion.setK1(0.2)

global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor

global targetL
targetL = 0.26235

global targetR
targetR = 0.249799

global targetmean
targetmean = (targetR+targetL)/2

global targettol
targettol = 0.02

global circleL #slow leg circle marker
circleL = vizshape.addSphere(0.01,50,50,color=viz.GREEN)
circleL.setPosition(-0.03,targetL,0)
circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global circleR #slow leg circle marker
circleR = vizshape.addSphere(0.01,50,50)
circleR.color(1,0.7,0)
circleR.setPosition(0.04,targetR,0)
circleR.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global highlightr
highlightr = vizshape.addBox(size=[0.25,0.0175,0.001])
highlightr.color(0,0,1)
highlightr.setPosition(0.145,targetmean,0)
highlightr.disable(viz.LIGHTING)

global highlightl
highlightl = vizshape.addBox(size=[0.25,0.0175,0.001])
highlightl.color(0,0,1)
highlightl.setPosition(-0.135,targetmean,0)
highlightl.disable(viz.LIGHTING)

#setup order of highlights
short = -0.2*targetmean
long = 0.2*targetmean
med = 0
global frodo
shortFirst=1;
if (shortFirst == 1):
	frodo = [short]*10
	frodo = frodo + [med]*15
	frodo = frodo + [short]*15
	frodo = frodo + [med]*15
	frodo = frodo + [short]*25
	frodo = frodo + [med]*25
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [med]*50
elif (shortFirst == 0):
	frodo = [med]*10
	frodo = frodo + [short]*15
	frodo = frodo + [med]*15
	frodo = frodo + [short]*15
	frodo = frodo + [med]*25
	frodo = frodo + [short]*25
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
	frodo = frodo + [short]*50
	frodo = frodo + [med]*50
else:
	print('WARNING cannot determine first set please review...')

print(frodo)
global stepind
stepind = 0

highlightr.setPosition(0.145,targetmean+frodo[stepind],0)
highlightl.setPosition(-0.135,targetmean+frodo[stepind],0)

global Rclamp
Rclamp = 0

global Lclamp
Lclamp = 0

global randyclamps
randyclamps = (-0.04,-0.035,-0.03,-0.025,-0.02,-0.015,-0.01,-0.005,0,0.005,0.01,0.015,0.02,0.025,0.03,0.035,0.04)
#print(frodo)
#fakebox = vizshape.addBox(size=[1,0.01,0.001])
#fakebox.setPosition(0,targetmean,0)
#fakebox.color(0,1,0)
#fakebox.disable(viz.LIGHTING)

#create latitudinal grid, "10" is the target step length, the grid expands above and belo
lines = {}#create empty dictionary
for x in range(1,12,1):
	lines["Tp{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
	lines["Tp{0}".format(x)].setPosition(0,targetmean+0.05*targetmean+(x-1)*0.1*targetmean,0)#each gap represents 20 percent of target?
	lines["Tn{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
	lines["Tn{0}".format(x)].setPosition(0,targetmean+0.05*targetmean-(x-1)*0.1*targetmean,0)
#	print((x-1)*0.02)
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,targetmean-0.95*targetmean-0.1*targetmean+x*0.1*targetmean+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,targetmean-0.95*targetmean-0.1*targetmean+x*0.1*targetmean+0.005,0],scale=[0.015,0.015,0.015])
	
viz.MainView.setPosition(0,targetmean+0.05*targetmean, -0.57)
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
	global highlightl
	global highlightr
	global frodo
	global stepind
	global Rclamp
	global Lclamp
	global randyclamps
	
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
				RANKY = float(data["RANK"][1])/1000
				LANKY = float(data["LANK"][1])/1000
				RHIPY = float(data["RHIP"][1])/1000
				LHIPY = float(data["LHIP"][1])/1000
			except:
#				pass
				print(["ERROR: incorrect or missing marker data..."])

		
#		Rgamma = LANKY-RANKY
#		Lgamma = RANKY-LANKY
		
		Ralpha = (RHIPY+LHIPY)/2-RANKY
		Lalpha = (RHIPY+LHIPY)/2-LANKY
		
		#gait events
		if (Rz <= -30) & (histzR > -30):#RHS
			Rerror = Ralpha-(targetmean+frodo[stepind])
			RHS = 1
#			circleR.setPosition(0.05,targetmean+frodo[stepind]+random.choice(randyclamps),0)
#			circleR.setPosition(0.05,targetmean+frodo[stepind]+Rclamp[stepind],0)
			circleR.setPosition(0.05,targetmean+frodo[stepind]+0.35*Rerror,0)
			Rclamp = targetmean+frodo[stepind]+0.35*Rerror
			stepind = stepind+1
#			if (stepind > len(Rclamp)):
			if (stepind > 455):
				print('Task Complete! Out of steps')
			else:
				highlightr.setPosition(0.145,targetmean+frodo[stepind],0)
				highlightl.setPosition(-0.135,targetmean+frodo[stepind],0)
				
			if (Rerror < targettol):
				rgorb = 1
			else:
				rgorb = 0
#			nothing = updatetargetdisplay(Rgamma,circleR,2)
#		elif (Rz >-30) & (histzR<=-30): #RTO
#			highlightr.setPosition(0.145,targetmean+frodo(stepind),0)
		else:
			RHS = 0
			
		if (Lz <= -30) & (histzL > -30):#LHS
			Lerror = Lalpha-(targetmean+frodo[stepind])
			LHS = 1
#			if (stepind > len(Rclamp)):
			if (stepind > 455):
				print('Task Complete! Out of steps')
			else:
#				circleL.setPosition(-0.05,targetmean+frodo[stepind]+random.choice(randyclamps),0)
#				circleL.setPosition(-0.05,targetmean+frodo[stepind]+Lclamp[stepind],0)
				circleL.setPosition(-0.05,targetmean+frodo[stepind]+0.35*Lerror,0)
				Lclamp = targetmean+frodo[stepind]+0.35*Lerror

			if (Lerror < targettol):
				lgorb = 1
			else:
				lgorb = 0
#			targetnum = updatetargetdisplay(Lgamma,circleL,1)
		else:
			LHS = 0

		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,RANKY,LANKY,RHIPY,LHIPY,rgorb,lgorb,Ralpha,Lalpha,Rerror,Lerror,targetmean+frodo[stepind],Rclamp,Lclamp,]#organize the data to be written to file
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
#	print(data["DeviceCount"])
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
	mststring = str(mst2)+'EXP2B_V75_rev3_DK2.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','RANKY','LANKY','RHIPY','LHIPY','RGORB','LGORB','Ralpha','Lalpha','Rerror','Lerror','target','Rclamp','Lclamp'])
#	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','RANKY','LANKY','RGORB','LGORB','Rgamma','Lgamma','Rerror','Lerror','target','Rclamp','Lclamp'],file)
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
#t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
#t3.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
#t3.start()
t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	














>>>>>>> origin/master
