""" Biofeedback routine for step time, from HS to HS

This script updates left and right cursors based on step time, using a flip-flop technique

WDA 6/20/2016

rev7 introduces saving data

V2P DK2 R1
"""

import socket
import sys
import io
import re
#from xml.etree import ElementTree
#import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import subprocess
import csv

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe"')
#cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe"')
time.sleep(2)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)
time.sleep(3)
#set target tolerance for step time
global targetL
targetL = 0.7180

global targetR
targetR = 0.7180

global targettol
targettol = 0.025

global boxL
boxL = viz.addTexQuad(pos=[-0.2,targetL,0],scale=[0.2,2*targettol,0])
boxL.color(0,0.7,1)
boxL.alpha(0.7)
global boxR
boxR = viz.addTexQuad(pos=[0.2,targetR,0],scale=[0.2,2*targettol,0])
boxR.color(1,0.2,0)
boxR.alpha(0.7)

viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR-0.2,12])
#leftcounter = viz.addText(str(LCOUNT),pos=[-4.4,targetL-0.2,12])

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
HistBallR = viz.add('box.wrl', color=(2,2,0.7), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR+0.1,0])
HistBallR.alpha(0.8)
#HistBallR.visible(0)

global HistBallL
HistBallL = viz.add('box.wrl', color=(2,2,0.7), scale=[0.2,0.01,0.001], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)
#HistBallL.visible(0)

global histzR
histzR = 0
global histzL
histzL = 0
global steptime
steptime = 0

global rgorb#logic 1 on successful step, 0 if outside tolerance
rgorb = 0

global lgorb
lgorb = 0

global RHS 
RHS = 0

global LHS
LHS = 0


def UpdateViz(root,q,savestring,q3):
	global targetL
	global targetR
	global targettol
	global histzR
	global histzL
	global steptime
	global rgorb
	global lgorb
	global RHS
	global LHS
	timeold = time.time()
	
	while not endflag.isSet():
		root = q.get()
		timediff = time.time()-timeold
		
		data = ParseRoot(root)		
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		
		if (Rz < -30) & (histzR >= -30):#RHS
			cursorR.visible(0)# hide right side show left
			cursorL.visible(1)
			RHS = 1
			if (abs(steptime - targetR) < targettol):
				boxR.color(0,1,0.3)
				rgorb = 1
			else:
				boxR.color(1,0.2,0)
				rgorb = 0
			HistBallR.setPosition([0.2, steptime, 0])
			steptime = 0
		
		elif (Lz < -30) & (histzL >= -30): #LHS
			cursorR.visible(1)
			cursorL.visible(0)
			LHS = 1
			if (abs(steptime - targetL) < targettol):
				boxL.color(0,1,0.3)
				lgorb = 1
			else:
				boxL.color(1,0.2,0)
				lgorb = 0
			HistBallL.setPosition([-0.2, steptime, 0])
			steptime = 0
		else:
			RHS = 0
			LHS = 0
			steptime = steptime + timediff
		#change the heights
		cursorR.setScale(0.1,steptime,0.01250)
		cursorL.setScale(-0.1,steptime,0.01250)
		
		timeold = time.time()
		histzR = Rz
		histzL = Lz
		
		savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,steptime]
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
	mststring = str(mst2)+'BFback_steptime_rev7.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','rgorb','lgorb','steptime'])
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

endflag = threading.Event()
def raisestop(sign):
	print("stop flag raised")
	endflag.set()
	t1.join()
	t2.join()
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

vizact.onkeydown('q',raisestop,'biggle')