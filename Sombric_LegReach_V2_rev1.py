<<<<<<< HEAD
﻿#Oculus assisted leg reaching task, to be performed before and throughout the split belt paradigm
#
#Subjects see a static display which give cues about which target to reach for.
#V2 is the evaluation version where no biofeedback is shown, only which target to step to.
#
#William Anderton 4/22/2016
#V2P_DK2_R1

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
import vizfx.postprocess

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.go(
#viz.FULLSCREEN #run world in full screen
)

monoWindow = viz.addWindow(size=(1,1), pos=(0,1), scene=viz.addScene())
monoQuad = viz.addTexQuad(parent=viz.ORTHO, scene=monoWindow)
monoQuad.setBoxTransform(viz.BOX_ENABLED)
monoQuad.setTexQuadDisplayMode(viz.TEXQUAD_FILL)
texture = vizfx.postprocess.getEffectManager().getColorTexture()

def UpdateTexture():
    monoQuad.texture(texture)
vizact.onupdate(0, UpdateTexture)

global targettol
targettol = 0.02

global target
target = 0.22625

global transcale
transcale = 0.1/target

global LEG
LEG = 0 #0 for right leg, 1 for left

#declare the total number of steps to attempt each target
global STEPNUM
STEPNUM = 30

global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor
profile = hmd.getProfile()
hmd.setIPD(profile.ipd)

viz.MainView.setPosition(0, 0.1, -0.47)
viz.MainView.setEuler(0,0,0)

global sagt
sagt = vizshape.addBox(size=[0.04,0.02,0.01])
sagt.setPosition(0,0.1,0)
#sagt.color(0,0.7,1)
sagt.color(viz.GRAY)
sagt.disable(viz.LIGHTING)

global origin
#origin = vizshape.addSphere(0.01,20,20)
origin = viz.add('box3.obj',scale = [0.02,0.02,0.001],cache=viz.CACHE_NONE)
#origin.color(20,20,20)
origin.color(viz.GRAY)
origin.disable(viz.LIGHTING)
origin.setPosition(0,-0.01,0)

global latt
latt = vizshape.addBox(size=[0.02,0.04,0.01])
if (LEG==0):
	latt.setPosition(0.1,0,0)
else:
	latt.setPosition(-0.1,0,0)
#latt.color(0,0.7,1)
latt.color(viz.GRAY)
latt.disable(viz.LIGHTING)


global histzR
histzR = 0
global histzL
histzL = 0

global cursor
cursor = viz.add('box3.obj',scale=[0.005,0.005,0.005],cache=viz.CACHE_NONE)
#cursor.color(0,155,50)
cursor.color(viz.RED)
cursor.disable(viz.LIGHTING)
cursor.setPosition(0,0,-0.02)
cursor.visible(0)

global RTOEX
RTOEX = 0
global RTOEY
RTOEY = 0
global LTOEX
LTOEX = 0
global LTOEY
LTOEY = 0

global xoff
xoff = 0

global yoff
yoff = 0

global RHS #definition of HS is altered, it indicates when a force is present for a certain length of time.
RHS = 0
global LHS
LHS = 0
global rtouchx
rtouchx = 0
global ltouchx
ltouchx = 0
global rtouchy
rtouchy = 0
global ltouchy
ltouchy = 0

global touchdown
touchdown = 0

#make array of test order:
highlight = [1,3]*2*STEPNUM
print(highlight)

global stepind
stepind = 0

#highlight the current target
#if (highlight[stepind] == 1):
#	sagt.color(0,0.7,1)
#	origin.color(viz.GRAY)
#	latt.color(viz.GRAY)
#elif (highlight[stepind] == 2):
#	sagt.color(viz.GRAY)
#	origin.color(0,0.7,1)
#	latt.color(viz.GRAY)
#elif (highlight[stepind] == 3):
#	sagt.color(viz.GRAY)
#	origin.color(viz.GRAY)
#	latt.color(0,0.7,1)
#else:
#	print('error when attempting to highlight target...')

#setup array of randomly picked steps
#global randy
#randy = []
#order = [1,2] * (2*STEPNUM)
#while len(randy) < 20:#optimistically sample the solution space for test orders, reduced from 100 on 11/3/2015 to reduce calculation time for high stepnum
#    random.shuffle(order)
#    if order in randy:
#        continue
#    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
#        randy.append(order[:])
#randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
#print(randy)

global phase
phase = 500

global textwin
textwin = viz.addText('',pos=[0,0,-0.02],scale=[0.015,0.015,0.015])


def UpdateViz(root,q,savestring,q3):

	global histzL
	global histzR
	global cpps
	global targettol
	global RHS
	global LHS
	global STEPNUM
	global randy
	global LEG
	global target
	global targettol
	global RTOEX
	global RTOEY
	global LTOEX
	global LTOEY
	global xoff
	global yoff
	global transcale
	global RHS
	global LHS
	global rtouchx
	global ltouchx
	global rtouchy
	global ltouchy
	global touchdown
	global stepind
	global phase
	global textwin

	while not endflag.isSet():
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		#look for marker data

		RANKY = float(data["RANK"][1])/1000
		LANKY = float(data["LANK"][1])/1000
		RTOEX = float(data["RTOE"][0])/1000
		LTOEX = float(data["LTOE"][0])/1000
		RTOEY = float(data["RTOE"][1])/1000
		LTOEY = float(data["LTOE"][1])/1000
		
#		textwin.message(str(phase))
#		print(abs(LTOEX-RTOEX+xoff))
		
		if (stepind > STEPNUM):
			phase = 3
		
		if (phase == 0):#start at the origin box
			sagt.color(viz.GRAY)
			latt.color(viz.GRAY)
			origin.color(0,0.7,1)
#			print(touchdown)
			if (LEG == 0):
				cursor.setPosition(transcale*(LTOEX-RTOEX+xoff),transcale*(LTOEY-RTOEY+yoff),-0.02)
				if (transcale*abs(LTOEX-RTOEX+xoff)<0.05) & (transcale*abs(LTOEY-RTOEY+yoff)<0.05):
					cursor.visible(1)
				else:
					cursor.visible(0)				
				if (abs(LTOEX-RTOEX+xoff)<targettol) & (abs(LTOEY-RTOEY+yoff)<targettol) & (Rz < -50) & (Lz < -50) & (touchdown > 50):
					phase = 1
					if (highlight[stepind] == 1):
						sagt.color(0,0.7,1)
						origin.color(viz.GRAY)
						latt.color(viz.GRAY)
					elif (highlight[stepind] == 3):
						sagt.color(viz.GRAY)
						origin.color(viz.GRAY)
						latt.color(0,0.7,1)
					else:
						print('error when attempting to highlight target...')
				elif (abs(LTOEX-RTOEX+xoff)<targettol) & (abs(LTOEY-RTOEY+yoff)<targettol) & (Rz < -50) & (Lz < -50) :
					touchdown = touchdown +1
					
			elif (LEG == 1):
				cursor.setPosition(transcale*(RTOEX-LTOEX-xoff),transcale*(RTOEY-LTOEY-yoff),-0.02)
				if (transcale*abs(RTOEX-LTOEX-xoff)<0.05) & (transcale*abs(RTOEY-LTOEY-yoff)<0.05):
					cursor.visible(1)
				else:
					cursor.visible(0)				
				if (abs(RTOEX-LTOEX-xoff)<targettol) & (abs(RTOEY-LTOEY-yoff)<targettol) & (Rz < -50) & (Lz < -50) & (touchdown > 50):
					phase = 1
					if (highlight[stepind] == 1):
						sagt.color(0,0.7,1)
						origin.color(viz.GRAY)
						latt.color(viz.GRAY)
					elif (highlight[stepind] == 3):
						sagt.color(viz.GRAY)
						origin.color(viz.GRAY)
						latt.color(0,0.7,1)
					else:
						print('error when attempting to highlight target...')
				elif (abs(RTOEX-LTOEX-xoff)<targettol) & (abs(RTOEX-LTOEX-xoff)<targettol) & (Rz < -50) & (Lz < -50) :
					touchdown = touchdown +1
					
		elif (phase == 1):#wait for toe off
			cursor.visible(0)
			if (LEG == 0):
				cursor.setPosition(transcale*(LTOEX-RTOEX+xoff),transcale*(LTOEY-RTOEY+yoff),-0.02)
				touchdown = 0
				if (Rz >=-30) & (histzR <-30):
					phase = 2
			elif (LEG == 1):
				cursor.setPosition(transcale*(RTOEX-LTOEX-xoff),transcale*(RTOEY-LTOEY-yoff),-0.02)
				touchdown = 0
				if (Lz >=-30) & (histzL <-30):
					phase = 2
					
					
					
		elif (phase == 2):#look for step attempt
			
			if (LEG==0):
				cursor.setPosition(transcale*(LTOEX-RTOEX+xoff),transcale*(LTOEY-RTOEY+yoff),-0.02)
				#look for touch
				if (Rz <=-30) & (touchdown > 100): #touch must last 0.5 seconds
					RHS = 1
					rtouchx = (LTOEX-RTOEX+xoff)
					rtouchy = (LTOEY-RTOEY+yoff)
					touchdown = 0
					stepind = stepind + 1
					phase = 0
						
				elif (Rz <= -30):
					touchdown = touchdown+1
					RHS = 0
				else:
					touchdown = 0 #restart the counting
					RHS = 0
					rtouchx = (LTOEX-RTOEX+xoff)
					rtouchy = (LTOEY-RTOEY+yoff)
			elif (LEG==1):
				cursor.setPosition(transcale*(RTOEX-LTOEX-xoff),transcale*(RTOEY-LTOEY-yoff),-0.02)
				
				if (Lz <= -30) & (touchdown > 100):
					LHS = 1
					ltouchx = (RTOEX-LTOEX-xoff)
					ltouchy = (RTOEY-LTOEY-yoff)
					touchdown = 0
					stepind = stepind + 1
					phase = 0

				elif (Lz <= -30):
					touchdown = touchdown+1
					LHS = 0
				else:
					LHS = 0
					touchdown = 0 #restart the counting
					ltouchx = (RTOEX-LTOEX-xoff)
					ltouchy = (RTOEY-LTOEY-yoff)
		elif (phase==3):
			textwin.message('Test Complete!')
			savestring = [FN,Rz,Lz,RHS,LHS,rtouchx,ltouchx,rtouchy,ltouchy,phase,highlight[stepind],RTOEX,LTOEX,RTOEY,LTOEY,xoff,yoff]#organize the data to be written to file
			q3.put(savestring)
			break
		
		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,rtouchx,ltouchx,rtouchy,ltouchy,phase,highlight[stepind],RTOEX,LTOEX,RTOEY,LTOEY,xoff,yoff]#organize the data to be written to file
		q3.put(savestring)
			
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
	mststring = str(mst2)+'SombricLegReach_DK2_V2_rev1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','rtouchx','ltouchx','rtouchy','ltouchy','phase','highlight','RTOEX','LTOEX','RTOEY','LTOEY','xoffset','yoffset'])
	
#	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','rtouchx','ltouchx','rtouchy','ltouchy'],file)
	file.close()
	
	file = open(mststring,'a')#reopen for appending only
	csvw = csv.writer(file)
	while not endflag.isSet():
		savestring = q3.get()#look in the queue for data to write
	
		if savestring is None:
			continue
		else:
			csvw.writerow(savestring)
#			json.dump(savestring, file)
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
#			json.dump(savestring, file)
			print("data still writing to file")
		
	print("savedata finished writing")
	file.close()
	
def SetOrigin(biggle):
	global xoff
	global yoff
	global RTOEX
	global RTOEY
	global LTOEX
	global LTOEY
	global phase
	
	
	xoff = RTOEX-LTOEX
	yoff = RTOEY-LTOEY
	phase = 0
	
#	return(xoff,yoff)

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
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,savestring,q3))
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
#vizact.onkeydown('65461',SetOrigin,'biggle')# 65461 is #5 on the wireless keypad
vizact.onkeydown('r',SetOrigin,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback

=======
﻿#Oculus assisted leg reaching task, to be performed before and throughout the split belt paradigm
#
#Subjects see a static display which give cues about which target to reach for.
#V2 is the evaluation version where no biofeedback is shown, only which target to step to.
#
#William Anderton 4/22/2016
#V2P_DK2_R1

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
import vizfx.postprocess

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.go(
#viz.FULLSCREEN #run world in full screen
)

monoWindow = viz.addWindow(size=(1,1), pos=(0,1), scene=viz.addScene())
monoQuad = viz.addTexQuad(parent=viz.ORTHO, scene=monoWindow)
monoQuad.setBoxTransform(viz.BOX_ENABLED)
monoQuad.setTexQuadDisplayMode(viz.TEXQUAD_FILL)
texture = vizfx.postprocess.getEffectManager().getColorTexture()

def UpdateTexture():
    monoQuad.texture(texture)
vizact.onupdate(0, UpdateTexture)

global targettol
targettol = 0.02

global target
target = 0.22625

global transcale
transcale = 0.1/target

global LEG
LEG = 0 #0 for right leg, 1 for left

#declare the total number of steps to attempt each target
global STEPNUM
STEPNUM = 30

global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor
profile = hmd.getProfile()
hmd.setIPD(profile.ipd)

viz.MainView.setPosition(0, 0.1, -0.47)
viz.MainView.setEuler(0,0,0)

global sagt
sagt = vizshape.addBox(size=[0.04,0.02,0.01])
sagt.setPosition(0,0.1,0)
#sagt.color(0,0.7,1)
sagt.color(viz.GRAY)
sagt.disable(viz.LIGHTING)

global origin
#origin = vizshape.addSphere(0.01,20,20)
origin = viz.add('box3.obj',scale = [0.02,0.02,0.001],cache=viz.CACHE_NONE)
#origin.color(20,20,20)
origin.color(viz.GRAY)
origin.disable(viz.LIGHTING)
origin.setPosition(0,-0.01,0)

global latt
latt = vizshape.addBox(size=[0.02,0.04,0.01])
if (LEG==0):
	latt.setPosition(0.1,0,0)
else:
	latt.setPosition(-0.1,0,0)
#latt.color(0,0.7,1)
latt.color(viz.GRAY)
latt.disable(viz.LIGHTING)


global histzR
histzR = 0
global histzL
histzL = 0

global cursor
cursor = viz.add('box3.obj',scale=[0.005,0.005,0.005],cache=viz.CACHE_NONE)
#cursor.color(0,155,50)
cursor.color(viz.RED)
cursor.disable(viz.LIGHTING)
cursor.setPosition(0,0,-0.02)
cursor.visible(0)

global RTOEX
RTOEX = 0
global RTOEY
RTOEY = 0
global LTOEX
LTOEX = 0
global LTOEY
LTOEY = 0

global xoff
xoff = 0

global yoff
yoff = 0

global RHS #definition of HS is altered, it indicates when a force is present for a certain length of time.
RHS = 0
global LHS
LHS = 0
global rtouchx
rtouchx = 0
global ltouchx
ltouchx = 0
global rtouchy
rtouchy = 0
global ltouchy
ltouchy = 0

global touchdown
touchdown = 0

#make array of test order:
highlight = [1,3]*2*STEPNUM
print(highlight)

global stepind
stepind = 0

#highlight the current target
#if (highlight[stepind] == 1):
#	sagt.color(0,0.7,1)
#	origin.color(viz.GRAY)
#	latt.color(viz.GRAY)
#elif (highlight[stepind] == 2):
#	sagt.color(viz.GRAY)
#	origin.color(0,0.7,1)
#	latt.color(viz.GRAY)
#elif (highlight[stepind] == 3):
#	sagt.color(viz.GRAY)
#	origin.color(viz.GRAY)
#	latt.color(0,0.7,1)
#else:
#	print('error when attempting to highlight target...')

#setup array of randomly picked steps
#global randy
#randy = []
#order = [1,2] * (2*STEPNUM)
#while len(randy) < 20:#optimistically sample the solution space for test orders, reduced from 100 on 11/3/2015 to reduce calculation time for high stepnum
#    random.shuffle(order)
#    if order in randy:
#        continue
#    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
#        randy.append(order[:])
#randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
#print(randy)

global phase
phase = 500

global textwin
textwin = viz.addText('',pos=[0,0,-0.02],scale=[0.015,0.015,0.015])


def UpdateViz(root,q,savestring,q3):

	global histzL
	global histzR
	global cpps
	global targettol
	global RHS
	global LHS
	global STEPNUM
	global randy
	global LEG
	global target
	global targettol
	global RTOEX
	global RTOEY
	global LTOEX
	global LTOEY
	global xoff
	global yoff
	global transcale
	global RHS
	global LHS
	global rtouchx
	global ltouchx
	global rtouchy
	global ltouchy
	global touchdown
	global stepind
	global phase
	global textwin

	while not endflag.isSet():
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		
		#look for marker data

		RANKY = float(data["RANK"][1])/1000
		LANKY = float(data["LANK"][1])/1000
		RTOEX = float(data["RTOE"][0])/1000
		LTOEX = float(data["LTOE"][0])/1000
		RTOEY = float(data["RTOE"][1])/1000
		LTOEY = float(data["LTOE"][1])/1000
		
#		textwin.message(str(phase))
#		print(abs(LTOEX-RTOEX+xoff))
		
		if (stepind > STEPNUM):
			phase = 3
		
		if (phase == 0):#start at the origin box
			sagt.color(viz.GRAY)
			latt.color(viz.GRAY)
			origin.color(0,0.7,1)
#			print(touchdown)
			if (LEG == 0):
				cursor.setPosition(transcale*(LTOEX-RTOEX+xoff),transcale*(LTOEY-RTOEY+yoff),-0.02)
				if (transcale*abs(LTOEX-RTOEX+xoff)<0.05) & (transcale*abs(LTOEY-RTOEY+yoff)<0.05):
					cursor.visible(1)
				else:
					cursor.visible(0)				
				if (abs(LTOEX-RTOEX+xoff)<targettol) & (abs(LTOEY-RTOEY+yoff)<targettol) & (Rz < -50) & (Lz < -50) & (touchdown > 50):
					phase = 1
					if (highlight[stepind] == 1):
						sagt.color(0,0.7,1)
						origin.color(viz.GRAY)
						latt.color(viz.GRAY)
					elif (highlight[stepind] == 3):
						sagt.color(viz.GRAY)
						origin.color(viz.GRAY)
						latt.color(0,0.7,1)
					else:
						print('error when attempting to highlight target...')
				elif (abs(LTOEX-RTOEX+xoff)<targettol) & (abs(LTOEY-RTOEY+yoff)<targettol) & (Rz < -50) & (Lz < -50) :
					touchdown = touchdown +1
					
			elif (LEG == 1):
				cursor.setPosition(transcale*(RTOEX-LTOEX-xoff),transcale*(RTOEY-LTOEY-yoff),-0.02)
				if (transcale*abs(RTOEX-LTOEX-xoff)<0.05) & (transcale*abs(RTOEY-LTOEY-yoff)<0.05):
					cursor.visible(1)
				else:
					cursor.visible(0)				
				if (abs(RTOEX-LTOEX-xoff)<targettol) & (abs(RTOEY-LTOEY-yoff)<targettol) & (Rz < -50) & (Lz < -50) & (touchdown > 50):
					phase = 1
					if (highlight[stepind] == 1):
						sagt.color(0,0.7,1)
						origin.color(viz.GRAY)
						latt.color(viz.GRAY)
					elif (highlight[stepind] == 3):
						sagt.color(viz.GRAY)
						origin.color(viz.GRAY)
						latt.color(0,0.7,1)
					else:
						print('error when attempting to highlight target...')
				elif (abs(RTOEX-LTOEX-xoff)<targettol) & (abs(RTOEX-LTOEX-xoff)<targettol) & (Rz < -50) & (Lz < -50) :
					touchdown = touchdown +1
					
		elif (phase == 1):#wait for toe off
			cursor.visible(0)
			if (LEG == 0):
				cursor.setPosition(transcale*(LTOEX-RTOEX+xoff),transcale*(LTOEY-RTOEY+yoff),-0.02)
				touchdown = 0
				if (Rz >=-30) & (histzR <-30):
					phase = 2
			elif (LEG == 1):
				cursor.setPosition(transcale*(RTOEX-LTOEX-xoff),transcale*(RTOEY-LTOEY-yoff),-0.02)
				touchdown = 0
				if (Lz >=-30) & (histzL <-30):
					phase = 2
					
					
					
		elif (phase == 2):#look for step attempt
			
			if (LEG==0):
				cursor.setPosition(transcale*(LTOEX-RTOEX+xoff),transcale*(LTOEY-RTOEY+yoff),-0.02)
				#look for touch
				if (Rz <=-30) & (touchdown > 100): #touch must last 0.5 seconds
					RHS = 1
					rtouchx = (LTOEX-RTOEX+xoff)
					rtouchy = (LTOEY-RTOEY+yoff)
					touchdown = 0
					stepind = stepind + 1
					phase = 0
						
				elif (Rz <= -30):
					touchdown = touchdown+1
					RHS = 0
				else:
					touchdown = 0 #restart the counting
					RHS = 0
					rtouchx = (LTOEX-RTOEX+xoff)
					rtouchy = (LTOEY-RTOEY+yoff)
			elif (LEG==1):
				cursor.setPosition(transcale*(RTOEX-LTOEX-xoff),transcale*(RTOEY-LTOEY-yoff),-0.02)
				
				if (Lz <= -30) & (touchdown > 100):
					LHS = 1
					ltouchx = (RTOEX-LTOEX-xoff)
					ltouchy = (RTOEY-LTOEY-yoff)
					touchdown = 0
					stepind = stepind + 1
					phase = 0

				elif (Lz <= -30):
					touchdown = touchdown+1
					LHS = 0
				else:
					LHS = 0
					touchdown = 0 #restart the counting
					ltouchx = (RTOEX-LTOEX-xoff)
					ltouchy = (RTOEY-LTOEY-yoff)
		elif (phase==3):
			textwin.message('Test Complete!')
			savestring = [FN,Rz,Lz,RHS,LHS,rtouchx,ltouchx,rtouchy,ltouchy,phase,highlight[stepind],RTOEX,LTOEX,RTOEY,LTOEY,xoff,yoff]#organize the data to be written to file
			q3.put(savestring)
			break
		
		
		histzR = Rz
		histzL = Lz
		#save data
		savestring = [FN,Rz,Lz,RHS,LHS,rtouchx,ltouchx,rtouchy,ltouchy,phase,highlight[stepind],RTOEX,LTOEX,RTOEY,LTOEY,xoff,yoff]#organize the data to be written to file
		q3.put(savestring)
			
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
	mststring = str(mst2)+'SombricLegReach_DK2_V2_rev1.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','rtouchx','ltouchx','rtouchy','ltouchy','phase','highlight','RTOEX','LTOEX','RTOEY','LTOEY','xoffset','yoffset'])
	
#	json.dump(['FrameNumber','Rfz','Lfz','RHS','LHS','rtouchx','ltouchx','rtouchy','ltouchy'],file)
	file.close()
	
	file = open(mststring,'a')#reopen for appending only
	csvw = csv.writer(file)
	while not endflag.isSet():
		savestring = q3.get()#look in the queue for data to write
	
		if savestring is None:
			continue
		else:
			csvw.writerow(savestring)
#			json.dump(savestring, file)
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
#			json.dump(savestring, file)
			print("data still writing to file")
		
	print("savedata finished writing")
	file.close()
	
def SetOrigin(biggle):
	global xoff
	global yoff
	global RTOEX
	global RTOEY
	global LTOEX
	global LTOEY
	global phase
	
	
	xoff = RTOEX-LTOEX
	yoff = RTOEY-LTOEY
	phase = 0
	
#	return(xoff,yoff)

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
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,savestring,q3))
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
#vizact.onkeydown('65461',SetOrigin,'biggle')# 65461 is #5 on the wireless keypad
vizact.onkeydown('r',SetOrigin,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback

>>>>>>> origin/master
