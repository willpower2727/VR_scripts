<<<<<<< HEAD
﻿#This script is a test of a minimum jerk trajectory generator for moving a marker to a desired location on the treadmill
#
#WDA 2/18/2016
#
#Marker data is streamed like normal, on command, the script generates a MJT to move the marker to the desired location.

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
import numpy.matlib
import imp
oculus = imp.load_source('oculus', 'C:\Program Files\WorldViz\Vizard5\python\oculus.py')

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
time.sleep(2)

viz.go()

global startflag
startflag = 0

global old0 
old0 = 0
global old1
old1 = 0

def UpdateViz(root,q,speedlist,qq):
	
	def MJT(xi,xf,t):
		global startflag
		startflag = 0
		times = np.arange(0,t+0.2,0.2)
		a = np.matlib.repmat(xf-xi,max(times.shape),1)
		b = 10*np.power(np.divide(times,t),3)-15*np.power(np.divide(times,t),4)+6*np.power(np.divide(times,t),5)
		b = np.resize(b,(len(b),1))
		c = np.add(np.matlib.repmat(xi,max(times.shape),1),np.multiply(a,b.T))
		c = c[1,:]
#		d = np.multiply(np.ediff1d(c),1000)
		d = np.divide(np.ediff1d(c),0.2)
		d = np.append(d,0)
		d = d.astype(int)
#		print(d.shape)
#		print(d)
		return d
	
	while not endflag.isSet():
		global startflag		
		
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		#look for marker data
		try:
#			RANKY = float(data["RANK"][1])/1000
#			LANKY = float(data["LANK"][1])/1000
#			RHIPY = float(data["RGT"][1])/1000
#			LHIPY = float(data["LGT"][1])/1000
			PC1Y = float(data["PC1"][1])/1000
#			print(PC1Y)
		except:
			print(["ERROR: incorrect or missing marker data..."])

		if (startflag!=0):

			if (abs(1.45-PC1Y) >= 0.04):
				speedlist = [0,300,1300,1300,0]
				qq.put(speedlist)
				#generate MJT
#				out = MJT(PC1Y*1000,1.45*1000,2)
#
#				for x in range(0,len(out),1):
#					speedlist = [out[x],out[x],6000,6000,0]#the accelerations "1300 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
#					qq.put(speedlist)
#					time.sleep(0.2)
			else:
				speedlist = [0,0,2000,2000,0]
				qq.put(speedlist)
	#close cpp server
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
	
def SignalStart(nothing):
	global startflag
	print('startflag raised')
	startflag = 1
	
root = ''#empty string
#savestring = ''
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
#q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq))
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
#t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
t3.daemon = True
#t4.daemon = True
#start the threads
t1.start()
t2.start()
t3.start()
#t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
=======
﻿#This script is a test of a minimum jerk trajectory generator for moving a marker to a desired location on the treadmill
#
#WDA 2/18/2016
#
#Marker data is streamed like normal, on command, the script generates a MJT to move the marker to the desired location.

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
import numpy.matlib
import imp
oculus = imp.load_source('oculus', 'C:\Program Files\WorldViz\Vizard5\python\oculus.py')

global cpps
cpps = subprocess.Popen("C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev1/x64/Release/Vicon2Python_DK2_rev1.exe")
time.sleep(2)

viz.go()

global startflag
startflag = 0

global old0 
old0 = 0
global old1
old1 = 0

def UpdateViz(root,q,speedlist,qq):
	
	def MJT(xi,xf,t):
		global startflag
		startflag = 0
		times = np.arange(0,t+0.2,0.2)
		a = np.matlib.repmat(xf-xi,max(times.shape),1)
		b = 10*np.power(np.divide(times,t),3)-15*np.power(np.divide(times,t),4)+6*np.power(np.divide(times,t),5)
		b = np.resize(b,(len(b),1))
		c = np.add(np.matlib.repmat(xi,max(times.shape),1),np.multiply(a,b.T))
		c = c[1,:]
#		d = np.multiply(np.ediff1d(c),1000)
		d = np.divide(np.ediff1d(c),0.2)
		d = np.append(d,0)
		d = d.astype(int)
#		print(d.shape)
#		print(d)
		return d
	
	while not endflag.isSet():
		global startflag		
		
		root = q.get()#look for the next frame data in the thread queue
		data = ParseRoot(root)
		FN = int(data["FN"])
		Rz = float(data["Rz"])
		Lz = float(data["Lz"])
		#look for marker data
		try:
#			RANKY = float(data["RANK"][1])/1000
#			LANKY = float(data["LANK"][1])/1000
#			RHIPY = float(data["RGT"][1])/1000
#			LHIPY = float(data["LGT"][1])/1000
			PC1Y = float(data["PC1"][1])/1000
#			print(PC1Y)
		except:
			print(["ERROR: incorrect or missing marker data..."])

		if (startflag!=0):

			if (abs(1.45-PC1Y) >= 0.04):
				speedlist = [0,300,1300,1300,0]
				qq.put(speedlist)
				#generate MJT
#				out = MJT(PC1Y*1000,1.45*1000,2)
#
#				for x in range(0,len(out),1):
#					speedlist = [out[x],out[x],6000,6000,0]#the accelerations "1300 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
#					qq.put(speedlist)
#					time.sleep(0.2)
			else:
				speedlist = [0,0,2000,2000,0]
				qq.put(speedlist)
	#close cpp server
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
	
def SignalStart(nothing):
	global startflag
	print('startflag raised')
	startflag = 1
	
root = ''#empty string
#savestring = ''
speedlist = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
#q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq))
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
#t4 = threading.Thread(target=savedata,args=(savestring,q3))
t1.daemon = True
t2.daemon = True
t3.daemon = True
#t4.daemon = True
#start the threads
t1.start()
t2.start()
t3.start()
#t4.start()
	
print("\n")
print("press 'q' to stop")

vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
>>>>>>> origin/master
vizact.onkeydown('t',SignalStart,'biggelo')