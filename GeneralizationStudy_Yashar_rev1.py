<<<<<<< HEAD
﻿#This script displays real time biofeedback on Step Length 
#targets are time invariant values determined from the worst stroke patient
#static targets means that both legs can have different targets but the visual targets look the same
#i.e. try to walk with baseline symmetry, or walk with 0.2 assymetry
#
#WDA 11/23/2015
#
#Requirements:
#
#Nexus 1.x or 2.x
#system config: MAR_BF_DEFAULT
#
# 
#
#Rev 5 uses the new color scheme, and discontinues forced perspective on the targets, now targets can show thir true relations (one can be higher than the other)
#
#Use V2P_DK2_R1

import viz
import time
import socket
import sys
import io
import re
import threading
import Queue
import json
import vizact
import vizinfo
import random
import itertools
import struct
import array
import math
import scipy
import numpy as np
import oculus
import vizmat
import vizlens
import os.path
import subprocess
from numpy import matrix
from numpy import linalg

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe"')
time.sleep(2)


viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN #run world in full screen
)
time.sleep(2)#show off our cool logo, not really required but cool

#viz.startLayer(viz.LINES) 
#viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,-0.25,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-1,0,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,0,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(0.2,-0.5,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(-0.2,-0.5,-0.0001) 
#myLines = viz.endLayer() 

Eyedistance = -1.5
viz.MainView.setPosition(0,0.25,Eyedistance)
viz.MainView.setEuler(0,0,0)

global faketarget #asthetic value, arbitrarily chosen to look good, cursor will be scaled to hit this value when perfect assymetry is achieved.
faketarget = 0.25 #DO NOT CHANGE!!!!

#set target tolerance for ANK-ANK length at HS
global targetR
targetR = 0.5
global targetL
targetL = 0.5

global psudoR
psudoR = 1
global psudoL
psudoL = 1

global targettol
targettol = 0.05/2

global dummyR # dummy is a list
dummyR = [0]*5

global dummyL
dummyL = [0]*5


global rscale # values to scale cursor with, so that perfect hit lands in middle of faketarget
rscale = faketarget/(targetR)
#print('rscale: ',rscale)
global lscale
lscale = faketarget/(targetL)


global distheta#the view angles we'll need later
distheta = 2*math.atan2(2*targettol,2*abs(Eyedistance))

global distLZ
distLZ = (lscale*2*targettol)/(2*math.tan(distheta/2))

global distRZ
distRZ = (rscale*2*targettol)/(2*math.tan(distheta/2))

global widetheta
widetheta = 2*math.atan2(0.2,2*abs(Eyedistance))


global wideRX
wideRX = 2*(distRZ)*math.tan(widetheta/2)

global distRX
distRX = 2*distRZ*math.tan(widetheta/2)

global wideLX
wideLX = 2*(distLZ)*math.tan(widetheta/2)

global distLX
#distLX = wideLX/(2*math.tan(widetheta/2))
distLX = 2*distLZ*math.tan(widetheta/2)


#print(' wideLX: ',wideLX,'wideRX',wideRX)

#viz.startLayer(viz.LINES) 
#viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,-0.25,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-1,0,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,0,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(0.2,-0.5,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(-0.2,-0.5,-0.0001) 
#myLines = viz.endLayer() 

global boxL
boxL = viz.addTexQuad(pos=[-0.2,faketarget,0],scale=[0.2,2*targettol,0])
boxL.color(0,0.7,1)
boxL.alpha(0.7)
global boxR
boxR = viz.addTexQuad(pos=[0.2,faketarget,0],scale=[0.2,2*targettol,0])
#boxR.color(0,0.7,1)
#boxR.color(0,1,0.3)
boxR.color(1,0.2,0)
boxR.alpha(0.7)


global HistBallR
HistBallR = viz.add('box.wrl', color=(2,2,0.7), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.alpha(0.8)
#HistBallR.visible(0)

global HistBallL
HistBallL = viz.add('box.wrl', color=(2,2,0.7), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)
#HistBallL.visible(0)

global cursorR
#cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorR = viz.add('box3.obj', scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
#cursorR.setPosition([0.2,-1*faketarget,0])
cursorR.color(0.5,0.5,0.5)
#cursorR.setPosition([0.2,0,0])
cursorR.setPosition([distRX,0,Eyedistance+distRZ])
cursorR.disable(viz.LIGHTING)#we want unrealistic lighting to avoid perspective

global cursorL
#cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorL = viz.add('box3.obj', scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
cursorL.color(0.5,0.5,0.5)
#cursorL.setPosition([-0.2,-1*faketarget,0])
#cursorL.setPosition([-0.2,0,0])
cursorL.setPosition([-distLX,0,Eyedistance+distLZ])
cursorL.disable(viz.LIGHTING)


#setup counter panels
#global RCOUNT
#global LCOUNT
#RCOUNT = 0
#LCOUNT = 0
##rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
#rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR-0.2,12])
##leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
#leftcounter = viz.addText(str(LCOUNT),pos=[-4.4,targetL-0.2,12])

global Rforceold
global Lforceold
Rforceold = 0
Lforceold = 0

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

global RHS
RHS = 0
global LHS
LHs = 0

global rgorb
rgorb = 0
global lgorb
lgorb = 0

global rattempts
global lattempts
rattempts = 0
lattempts = 0

global rscore
global lscore
rscore = 0
lscore = 0

global tempR
tempR = [0]
global tempL
tempL = [0]


def UpdateViz(root,q,speedlist,qq,savestring,q3):

	while not endflag.isSet():
		global cursorR
		global cursorL
		global HistBallR
		global HistBallL
		global targettol
		global targetR
		global targetL
		global steplengthL
		global steplengthR
		global Rforceold
		global Lforceold
		global RHS
		global LHS
		global rscale
		global lscale
		global rgorb
		global lgorb
		global rattempts
		global lattempts
		global rscore
		global lscore
		global psudoR
		global psudoL
		global dummyR
		global dummyL
		global faketarget
		global distLZ
		global distRZ
		global wideLX
		global wideRX
		global distLX
		global distRX
		global tempR
		global tempL

		
		root = q.get()
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		if (len(data) < 8):
			print('WARNING data missing from the stream, skipping this frame...')
		else:
			RANKY = float(data["RANK"][1])/1000
			LANKY = float(data["LANK"][1])/1000
#		print Rz
#		try:
#			RHIPY = float(data["RHIP"][1])/1000
#			LHIPY = float(data["LHIP"][1])/1000
#		except:
#			RHIPY = float(data["RGT"][1])/1000
#			LHIPY = float(data["LGT"][1])/1000

#		print('RANKY: ',RANKY, ' LANKY: ',LANKY)
		
		if (LANKY-RANKY > 0) & (Rz > -10):#only visible in swing phase
			cursorR.visible(1)
		else:
			cursorR.visible(0)
			
		if (RANKY-LANKY > 0) & (Lz > -10):
			cursorL.visible(1)
		else:
			cursorL.visible(0)
			
		cursorR.setScale(wideRX,rscale*(LANKY-RANKY),0.001)
		cursorL.setScale(wideLX,lscale*(RANKY-LANKY),0.001)
		#RHS
		if (Rforceold >= -30) & (Rz < -30):
			steplengthR = LANKY-RANKY
			
			if (LANKY == 0) | (RANKY == 0):
				
				dummyR.append(0)
				dummyR.pop(0)	
			
			else:
				
				dummyR.append(steplengthR)
				dummyR.pop(0)
				print dummyR
			

#			print('R error',abs(steplengthR-targetR))
			HistBallR.setPosition([distRX,rscale*steplengthR,Eyedistance+distRZ-0.001])
#			HistBallR.setPosition([0.2,-0.25+steplengthR*rscale,0])
			HistBallR.setScale([wideRX,rscale*0.01,0])
		
			if (psudoR == 6):
				tempR = dummyR
				while 0 in tempR:
					tempR.remove(0)
				print(tempR)
				steplengthR_new = sum(tempR)/len(tempR)
#				print steplengthR_new
				targetL = steplengthR_new
				lscale = faketarget/targetL
				distLZ = (lscale*2*targettol)/(2*math.tan(distheta/2))
				wideLX = 2*(distLZ)*math.tan(widetheta/2)
				#distLX = wideLX/(2*math.tan(widetheta/2))
				distLX = 2*distLZ*math.tan(widetheta/2)
				boxL.setPosition([-distLX,faketarget,Eyedistance+distLZ])
				boxL.setScale([wideLX,lscale*2*targettol,0])
				
				cursorL.setPosition([-distLX,0,Eyedistance+distLZ])
				cursorL.setScale(wideLX,lscale*(RANKY-LANKY),0.001)
				HistBallL.setPosition([-distLX,lscale*steplengthL,Eyedistance+distLZ-0.001])
				HistBallL.setScale([wideLX,lscale*0.01,0])
				
				psudoR = 1
				
			psudoR = psudoR+1
				
			RHS = 1
			rattempts += 1
			#biofeedback
			if (abs(steplengthR-targetR)<targettol):
				boxR.color(0,1,0.3)
				rgorb = 1
				rscore += 1
			else:
				boxR.color(1,0.2,0)
				rgorb = 0
			print('Rscore: ',rscore,'/',rattempts)
		elif (Rforceold <= -30) & (Rz > -30):#RTO
			boxR.color(0,0.7,1)
		else:
			RHS = 0
		
			
		#LHS
		if (Lforceold >= -30) & (Lz < -30):
			
			steplengthL = RANKY-LANKY
			
			if (LANKY == 0) | (RANKY == 0):
				
				dummyL.append(0)
				dummyL.pop(0)	
			
			else:
				
				dummyL.append(steplengthL)
				dummyL.pop(0)
				print dummyL

			HistBallL.setPosition([-distLX,lscale*steplengthL,Eyedistance+distLZ-0.001])
			HistBallL.setScale([wideLX,lscale*0.01,0])
			
			if (psudoL == 6):
				tempL = dummyL
				while 0 in tempL:
					tempL.remove(0)
				print(tempL)
				steplengthL_new = sum(tempL)/len(tempL)
#				print steplengthL_new
				targetR = steplengthL_new
				rscale = faketarget/targetR
				distRZ = (rscale*2*targettol)/(2*math.tan(distheta/2))
				wideRX = 2*(distRZ)*math.tan(widetheta/2)
				distRX = 2*distRZ*math.tan(widetheta/2)
				
				boxR.setPosition([distRX,faketarget,Eyedistance+distRZ])
				boxR.setScale([wideRX,rscale*2*targettol,0])
				

				cursorR.setPosition([distRX,0,Eyedistance+distRZ])
				cursorR.setScale(wideRX,rscale*(LANKY-RANKY),0.001)
				HistBallR.setPosition([distRX,rscale*steplengthR,Eyedistance+distRZ-0.001])
				HistBallR.setScale([wideRX,rscale*0.01,0])


				psudoL = 1
			psudoL = psudoL+1
			
			LHS = 1
			lattempts += 1
#			print('L error',abs(steplengthL-targetL))
			if (abs(steplengthL-targetL)<targettol):
				boxL.color(0,1,0.3)
				lgorb = 1
				lscore += 1
			else:
				boxL.color(1,0.2,0)
				lgorb = 0
			print('Lscore: ',lscore,'/',lattempts)
		elif (Lforceold <= -30) & (Lz > -30):#LTO
			boxL.color(0,0.7,1)
		else:
			LHS = 0
			
		
		Rforceold = Rz
		Lforceold = Lz
		
#		savestring = [FN,Rz,Lz,RHIPY,LHIPY,RANKY,LANKY,fast,slow,RHS,LHS]
		savestring = [FN,Rz,Lz,RANKY,LANKY,steplengthR,steplengthL,RHS,LHS,rgorb,lgorb]
		q3.put(savestring)
		
		#calculate step lengths
		
	cpps.kill()

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
	mststring = str(mst2)+'GeneralizationStudy_Yashar_rev1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
#	json.dump(['FrameNumber','Rfz','Lfz','RHIPy','LHIPy','RANky','LANKy','fastSLASYM','slowSLASYM','RHS','LHS'],file)
	json.dump(['FrameNumber','Rfz','Lfz','RANky','LANKy','steplengthR','steplengthL','RHS','LHS','Rgorb','Lgorb'],file)
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
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq,savestring,q3))
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
﻿#This script displays real time biofeedback on Step Length 
#targets are time invariant values determined from the worst stroke patient
#static targets means that both legs can have different targets but the visual targets look the same
#i.e. try to walk with baseline symmetry, or walk with 0.2 assymetry
#
#WDA 11/23/2015
#
#Requirements:
#
#Nexus 1.x or 2.x
#system config: MAR_BF_DEFAULT
#
# 
#
#Rev 5 uses the new color scheme, and discontinues forced perspective on the targets, now targets can show thir true relations (one can be higher than the other)
#
#Use V2P_DK2_R1

import viz
import time
import socket
import sys
import io
import re
import threading
import Queue
import json
import vizact
import vizinfo
import random
import itertools
import struct
import array
import math
import scipy
import numpy as np
import oculus
import vizmat
import vizlens
import os.path
import subprocess
from numpy import matrix
from numpy import linalg

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe"')
time.sleep(2)


viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN #run world in full screen
)
time.sleep(2)#show off our cool logo, not really required but cool

#viz.startLayer(viz.LINES) 
#viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,-0.25,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-1,0,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,0,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(0.2,-0.5,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(-0.2,-0.5,-0.0001) 
#myLines = viz.endLayer() 

Eyedistance = -1.5
viz.MainView.setPosition(0,0.25,Eyedistance)
viz.MainView.setEuler(0,0,0)

global faketarget #asthetic value, arbitrarily chosen to look good, cursor will be scaled to hit this value when perfect assymetry is achieved.
faketarget = 0.25 #DO NOT CHANGE!!!!

#set target tolerance for ANK-ANK length at HS
global targetR
targetR = 0.5
global targetL
targetL = 0.5

global psudoR
psudoR = 1
global psudoL
psudoL = 1

global targettol
targettol = 0.05/2

global dummyR # dummy is a list
dummyR = [0]*5

global dummyL
dummyL = [0]*5


global rscale # values to scale cursor with, so that perfect hit lands in middle of faketarget
rscale = faketarget/(targetR)
#print('rscale: ',rscale)
global lscale
lscale = faketarget/(targetL)


global distheta#the view angles we'll need later
distheta = 2*math.atan2(2*targettol,2*abs(Eyedistance))

global distLZ
distLZ = (lscale*2*targettol)/(2*math.tan(distheta/2))

global distRZ
distRZ = (rscale*2*targettol)/(2*math.tan(distheta/2))

global widetheta
widetheta = 2*math.atan2(0.2,2*abs(Eyedistance))


global wideRX
wideRX = 2*(distRZ)*math.tan(widetheta/2)

global distRX
distRX = 2*distRZ*math.tan(widetheta/2)

global wideLX
wideLX = 2*(distLZ)*math.tan(widetheta/2)

global distLX
#distLX = wideLX/(2*math.tan(widetheta/2))
distLX = 2*distLZ*math.tan(widetheta/2)


#print(' wideLX: ',wideLX,'wideRX',wideRX)

#viz.startLayer(viz.LINES) 
#viz.vertex(-1,-0.25,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,-0.25,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-1,0,-0.0001) #Vertices are split into pairs. 
#viz.vertex(1,0,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(0.2,-0.5,-0.0001) 
#myLines = viz.endLayer()
#
#viz.startLayer(viz.LINES) 
#viz.vertex(-0.2,0.5,-0.0001) #Vertices are split into pairs. 
#viz.vertex(-0.2,-0.5,-0.0001) 
#myLines = viz.endLayer() 

global boxL
boxL = viz.addTexQuad(pos=[-0.2,faketarget,0],scale=[0.2,2*targettol,0])
boxL.color(0,0.7,1)
boxL.alpha(0.7)
global boxR
boxR = viz.addTexQuad(pos=[0.2,faketarget,0],scale=[0.2,2*targettol,0])
#boxR.color(0,0.7,1)
#boxR.color(0,1,0.3)
boxR.color(1,0.2,0)
boxR.alpha(0.7)


global HistBallR
HistBallR = viz.add('box.wrl', color=(2,2,0.7), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.alpha(0.8)
#HistBallR.visible(0)

global HistBallL
HistBallL = viz.add('box.wrl', color=(2,2,0.7), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)
#HistBallL.visible(0)

global cursorR
#cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorR = viz.add('box3.obj', scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
#cursorR.setPosition([0.2,-1*faketarget,0])
cursorR.color(0.5,0.5,0.5)
#cursorR.setPosition([0.2,0,0])
cursorR.setPosition([distRX,0,Eyedistance+distRZ])
cursorR.disable(viz.LIGHTING)#we want unrealistic lighting to avoid perspective

global cursorL
#cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.25,0.001], cache=viz.CACHE_NONE)
cursorL = viz.add('box3.obj', scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
cursorL.color(0.5,0.5,0.5)
#cursorL.setPosition([-0.2,-1*faketarget,0])
#cursorL.setPosition([-0.2,0,0])
cursorL.setPosition([-distLX,0,Eyedistance+distLZ])
cursorL.disable(viz.LIGHTING)


#setup counter panels
#global RCOUNT
#global LCOUNT
#RCOUNT = 0
#LCOUNT = 0
##rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
#rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR-0.2,12])
##leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
#leftcounter = viz.addText(str(LCOUNT),pos=[-4.4,targetL-0.2,12])

global Rforceold
global Lforceold
Rforceold = 0
Lforceold = 0

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

global RHS
RHS = 0
global LHS
LHs = 0

global rgorb
rgorb = 0
global lgorb
lgorb = 0

global rattempts
global lattempts
rattempts = 0
lattempts = 0

global rscore
global lscore
rscore = 0
lscore = 0

global tempR
tempR = [0]
global tempL
tempL = [0]


def UpdateViz(root,q,speedlist,qq,savestring,q3):

	while not endflag.isSet():
		global cursorR
		global cursorL
		global HistBallR
		global HistBallL
		global targettol
		global targetR
		global targetL
		global steplengthL
		global steplengthR
		global Rforceold
		global Lforceold
		global RHS
		global LHS
		global rscale
		global lscale
		global rgorb
		global lgorb
		global rattempts
		global lattempts
		global rscore
		global lscore
		global psudoR
		global psudoL
		global dummyR
		global dummyL
		global faketarget
		global distLZ
		global distRZ
		global wideLX
		global wideRX
		global distLX
		global distRX
		global tempR
		global tempL

		
		root = q.get()
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		if (len(data) < 8):
			print('WARNING data missing from the stream, skipping this frame...')
		else:
			RANKY = float(data["RANK"][1])/1000
			LANKY = float(data["LANK"][1])/1000
#		print Rz
#		try:
#			RHIPY = float(data["RHIP"][1])/1000
#			LHIPY = float(data["LHIP"][1])/1000
#		except:
#			RHIPY = float(data["RGT"][1])/1000
#			LHIPY = float(data["LGT"][1])/1000

#		print('RANKY: ',RANKY, ' LANKY: ',LANKY)
		
		if (LANKY-RANKY > 0) & (Rz > -10):#only visible in swing phase
			cursorR.visible(1)
		else:
			cursorR.visible(0)
			
		if (RANKY-LANKY > 0) & (Lz > -10):
			cursorL.visible(1)
		else:
			cursorL.visible(0)
			
		cursorR.setScale(wideRX,rscale*(LANKY-RANKY),0.001)
		cursorL.setScale(wideLX,lscale*(RANKY-LANKY),0.001)
		#RHS
		if (Rforceold >= -30) & (Rz < -30):
			steplengthR = LANKY-RANKY
			
			if (LANKY == 0) | (RANKY == 0):
				
				dummyR.append(0)
				dummyR.pop(0)	
			
			else:
				
				dummyR.append(steplengthR)
				dummyR.pop(0)
				print dummyR
			

#			print('R error',abs(steplengthR-targetR))
			HistBallR.setPosition([distRX,rscale*steplengthR,Eyedistance+distRZ-0.001])
#			HistBallR.setPosition([0.2,-0.25+steplengthR*rscale,0])
			HistBallR.setScale([wideRX,rscale*0.01,0])
		
			if (psudoR == 6):
				tempR = dummyR
				while 0 in tempR:
					tempR.remove(0)
				print(tempR)
				steplengthR_new = sum(tempR)/len(tempR)
#				print steplengthR_new
				targetL = steplengthR_new
				lscale = faketarget/targetL
				distLZ = (lscale*2*targettol)/(2*math.tan(distheta/2))
				wideLX = 2*(distLZ)*math.tan(widetheta/2)
				#distLX = wideLX/(2*math.tan(widetheta/2))
				distLX = 2*distLZ*math.tan(widetheta/2)
				boxL.setPosition([-distLX,faketarget,Eyedistance+distLZ])
				boxL.setScale([wideLX,lscale*2*targettol,0])
				
				cursorL.setPosition([-distLX,0,Eyedistance+distLZ])
				cursorL.setScale(wideLX,lscale*(RANKY-LANKY),0.001)
				HistBallL.setPosition([-distLX,lscale*steplengthL,Eyedistance+distLZ-0.001])
				HistBallL.setScale([wideLX,lscale*0.01,0])
				
				psudoR = 1
				
			psudoR = psudoR+1
				
			RHS = 1
			rattempts += 1
			#biofeedback
			if (abs(steplengthR-targetR)<targettol):
				boxR.color(0,1,0.3)
				rgorb = 1
				rscore += 1
			else:
				boxR.color(1,0.2,0)
				rgorb = 0
			print('Rscore: ',rscore,'/',rattempts)
		elif (Rforceold <= -30) & (Rz > -30):#RTO
			boxR.color(0,0.7,1)
		else:
			RHS = 0
		
			
		#LHS
		if (Lforceold >= -30) & (Lz < -30):
			
			steplengthL = RANKY-LANKY
			
			if (LANKY == 0) | (RANKY == 0):
				
				dummyL.append(0)
				dummyL.pop(0)	
			
			else:
				
				dummyL.append(steplengthL)
				dummyL.pop(0)
				print dummyL

			HistBallL.setPosition([-distLX,lscale*steplengthL,Eyedistance+distLZ-0.001])
			HistBallL.setScale([wideLX,lscale*0.01,0])
			
			if (psudoL == 6):
				tempL = dummyL
				while 0 in tempL:
					tempL.remove(0)
				print(tempL)
				steplengthL_new = sum(tempL)/len(tempL)
#				print steplengthL_new
				targetR = steplengthL_new
				rscale = faketarget/targetR
				distRZ = (rscale*2*targettol)/(2*math.tan(distheta/2))
				wideRX = 2*(distRZ)*math.tan(widetheta/2)
				distRX = 2*distRZ*math.tan(widetheta/2)
				
				boxR.setPosition([distRX,faketarget,Eyedistance+distRZ])
				boxR.setScale([wideRX,rscale*2*targettol,0])
				

				cursorR.setPosition([distRX,0,Eyedistance+distRZ])
				cursorR.setScale(wideRX,rscale*(LANKY-RANKY),0.001)
				HistBallR.setPosition([distRX,rscale*steplengthR,Eyedistance+distRZ-0.001])
				HistBallR.setScale([wideRX,rscale*0.01,0])


				psudoL = 1
			psudoL = psudoL+1
			
			LHS = 1
			lattempts += 1
#			print('L error',abs(steplengthL-targetL))
			if (abs(steplengthL-targetL)<targettol):
				boxL.color(0,1,0.3)
				lgorb = 1
				lscore += 1
			else:
				boxL.color(1,0.2,0)
				lgorb = 0
			print('Lscore: ',lscore,'/',lattempts)
		elif (Lforceold <= -30) & (Lz > -30):#LTO
			boxL.color(0,0.7,1)
		else:
			LHS = 0
			
		
		Rforceold = Rz
		Lforceold = Lz
		
#		savestring = [FN,Rz,Lz,RHIPY,LHIPY,RANKY,LANKY,fast,slow,RHS,LHS]
		savestring = [FN,Rz,Lz,RANKY,LANKY,steplengthR,steplengthL,RHS,LHS,rgorb,lgorb]
		q3.put(savestring)
		
		#calculate step lengths
		
	cpps.kill()

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
	mststring = str(mst2)+'GeneralizationStudy_Yashar_rev1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
#	json.dump(['FrameNumber','Rfz','Lfz','RHIPy','LHIPy','RANky','LANKy','fastSLASYM','slowSLASYM','RHS','LHS'],file)
	json.dump(['FrameNumber','Rfz','Lfz','RANky','LANKy','steplengthR','steplengthL','RHS','LHS','Rgorb','Lgorb'],file)
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
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq,savestring,q3))
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
	