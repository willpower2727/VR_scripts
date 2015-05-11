#script runs biofeedback routine with python c++ server

#revision 9    3/17/2015   WDA, is adjusted to work with the new V2P_rev2 (faster)

import socket
import sys
import io
import re
#from xml.etree import ElementTree
import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
import math
import cProfile
import pstats

'''
#cProfile.run('re.compile("viz.go()")')
def enable_thread_profiling():
	#Monkey-patch Thread.run to enable global profiling.
	#Each thread creates a local profiler; statistics are pooled
	#to the global stats object on run completion.
	threading.Thread.stats = None
	thread_run = threading.Thread.run

	def profile_run(self):
		self._prof = cProfile.Profile()
		self._prof.enable()
		thread_run(self)
		self._prof.disable()

		if threading.Thread.stats is None:
			threading.Thread.stats = pstats.Stats(self._prof)
		else:
			threading.Thread.stats.add(self._prof)

	threading.Thread.run = profile_run

def get_thread_stats():
	stats = getattr(threading.Thread, 'stats', None)
	if stats is None:
		raise ValueError, 'Thread profiling was not enabled,''or no threads finished running.'
	return stats
'''
viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(

viz.FULLSCREEN #run world in full screen
)
time.sleep(2)
#indicate flag for post-catch targets, which last for the first 12 steps
global catchflag
catchflag = 0
global stridecounter
stridecounter = 0

#set target tolerance for stride length
global targetL
targetL = 0.249
global targetR
targetR = 0.2508

#R Rigth leg 
global R
R = 1.244
#R left leg
global R2
R2 = 1.212

global targettol
targettol = 0.025

global boxL
boxL = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.2,0.005,targettol*2])
boxL.setPosition([-0.2,targetL,0])
boxL.setEuler(0,90,0)
global boxR
boxR = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.2,0.005,targettol*2])
boxR.setPosition([0.2,targetR,0])
boxR.setEuler(0,90,0)

viz.MainView.setPosition(0, 0.25, -1.25)
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
		global Rlist
		global Llist
		
		#get some data
		root = q.get()
		
		#find the data we need from the frame packet
		lp1 = root.find(".//FP_0/SubF_7/Fz")#Left Treadmill
		rp1 = root.find(".//FP_1/SubF_7/Fz")#Right Treadmill
		s0rhipy = root.find(".//Sub0/RHIP/Y")
		s0lhipy = root.find(".//Sub0/LHIP/Y")
		s0ranky = root.find(".//Sub0/RANK/Y")
		s0lanky = root.find(".//Sub0/LANK/Y")

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
		
		cursorR.setScale(0.1,-1*(RANKY-RHIPY),0.01250)
		cursorL.setScale(-0.1,-1*(LANKY-LHIPY),0.01250)
		
		#determine if we need to hide the cursor
		if (RHIPY-RANKY < 0) | (Rz < -30):
			cursorR.visible(0)
		else:
			cursorR.visible(1)
		if (LHIPY-LANKY < 0) | (Lz < -30):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
		
		if (catchflag == 0) | (stridecounter > 12):
			if (Rz <= -30) & (histzR > -30): #RHS condition
				HistBallR.setPosition([0.2,-1*(RANKY-RHIPY), 0])#update yellow history ball when HS happens
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
					boxR.color( viz.WHITE )
				else:
					Rgorb = 0
					boxR.color( viz.BLUE )
			elif (Rz >= -30) & (histzR < -30):#RTO
				#calculate Toe-Off position
				Rtop = RHIPY-RANKY
				RHS = 0
				if (psudoR >= 5): #if it's time to update target value
	#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
					targetR = abs(Rhsp)+(1/(1+R))*(abs(Rtop)-(R*abs(Rhsp)))
					Rlist.append(targetR)
					Rlist.pop(0)
					print('targetR')
					print(targetR)
					psudoR = 1
					boxR.setPosition([0.2,targetR,0])
			else:
				RHS = 0
				
			if (Lz <= -30) & (histzL > -30): #RHS condition
				HistBallL.setPosition([-0.2,LHIPY-LANKY, 0])#update yellow history ball when HS happens
				steplengthL = LHIPY-LANKY
				stridecounter = stridecounter+1#this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
				Lhsp = LHIPY-LANKY
				psudoL = psudoL +1
				LHS = 1
				#if successful step was taken, keep track of it
				if (abs(steplengthL-targetL) <= targettol):
					LCOUNT = LCOUNT+1
					leftcounter.message(str(LCOUNT))
					Lgorb = 1  #flag this step as good or bad
					boxL.color( viz.WHITE )
				else:
					Lgorb = 0
					boxL.color( viz.BLUE )
			elif (Lz >= -30) & (histzL < -30):#LTO
				#calculate Toe-Off position
				Ltop = LHIPY-LANKY
				LHS = 0
				if (psudoL >= 5): #if it's time to update target value
	#				targetR = 0.5*(abs(Rtop)+abs(Rhsp))
					targetL = abs(Lhsp)+(1/(1+R2))*(abs(Ltop)-(R2*abs(Lhsp)))
					Llist.append(targetL)
					Llist.pop(0)
					print('targetL')
					print(targetL)
					psudoL = 1
					boxL.setPosition([-0.2,targetL,0])
			else:
				LHS = 0
			
		elif (catchflag == 1) & (stridecounter <=12):
			if (Rz <= -30) & (histzR > -30): #RHS condition
				HistBallR.setPosition([0.2,-1*(RANKY-RHIPY), 0])#update yellow history ball when HS happens
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
					boxR.color( viz.WHITE )
				else:
					Rgorb = 0
					boxR.color( viz.BLUE )
			elif (Rz >= -30) & (histzR < -30):#RTO
				#calculate Toe-Off position
				Rtop = RHIPY-RANKY
				RHS = 0
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
			
			if (Lz <= -30) & (histzL > -30): #RHS condition
				HistBallL.setPosition([-0.2,LHIPY-LANKY, 0])#update yellow history ball when HS happens
				steplengthL = LHIPY-LANKY
				stridecounter = stridecounter+1#this line of code will not appear in Left foot section, as we want 12 strides after catch for each side
				Lhsp = LHIPY-LANKY
				psudoL = psudoL +1
				LHS = 1
				#if successful step was taken, keep track of it
				if (abs(steplengthL-targetL) <= targettol):
					LCOUNT = LCOUNT+1
					leftcounter.message(str(LCOUNT))
					Lgorb = 1  #flag this step as good or bad
					boxL.color( viz.WHITE )
				else:
					Lgorb = 0
					boxL.color( viz.BLUE )
			elif (Lz >= -30) & (histzL < -30):#LTO
				#calculate Toe-Off position
				Ltop = LHIPY-LANKY
				LHS = 0
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
		
		histzR = Rz
		histzL = Lz

		#send some data to be saved
		fn = root.find(".//FN")#find the frame number
		fnn = fn.attrib.values()
#		print(fnn[0])

		savestring = [int(fnn[0]),Rz,Lz,RHS,LHS,Rgorb,Lgorb,RHIPY-RANKY,LHIPY-LANKY,targetR,targetL,RHIPY,LHIPY,RANKY,LANKY]#organize the data to be written to file
#		print(sys.getsizeof(savestring))
		q3.put(savestring)

#	q3.join()
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
#			print(sys.getsizeof(databuf))
#			print(databuf)
			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
#			root = xml.etree.cElementTree(xml.etree.ElementTree.fromstring(databuf))
			fn = root.find(".//FN")#find the frame number
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
#	get_thread_stats().sort_stats('line')
#	get_thread_stats().print_stats()
	
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
#enable_thread_profiling()
t1.start()
t2.start()
t4.start()

print("\n")
print("press 'q' to stop")
print("\n")
vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
	