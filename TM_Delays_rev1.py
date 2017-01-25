""" A script to test the effect of treadmill delays on final position

Moves a weighted object to various reference positions at various speeds and records the final position

WDA 1/25/2017

V2P_DK2_R2

"""
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
import csv
import threading
import Queue
import time
import vizact
import struct
import array
import math
import subprocess
import vizfx
import vizact
import time 

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/PyAdaptVicon2Python/x64/Release/PyAdaptVicon2Python.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
viz.go(
#viz.FULLSCREEN #run world in full screen
)
global phase
phase = 0

global ind 
ind = 0

global target
target = [0.5,0.8,1.2]

global speed
speed = [300,100,50]

global speedind
speedind = 0

global SpdPak
SpdPak=()
##################################################################

def UpdateViz(root,q,speedlist,qq,savestring,q3,speedread,q4):
#	timeold = time.time()

	while not endflag.isSet():
		global phase
		global ind
		global Rspeed
		global Lspeed
		global SpdPak
		global speed
		global speedind
		
		if (q4.empty()==False) :
			SpdPak=q4.get()#1 is the right belt speed, 2 is the left belt speed; the treadmill comunicates in mm/s!
#			print('Length q4: ', q4.qsize() ,' RBS: ',SpdPak[1], 'LBS: ',SpdPak[2])
		
		root = q.get()#look for the next frame data in the thread queue
		if root is None:
			continue
		else:
			data = ParseRoot(root)
			FN = int(data["FN"])
			Rz = float(data["Rz"])
			Lz = float(data["Lz"])
			#look for marker data

			PC1 = float(data["HANDp"][1])/1000

			if (phase == 0): #move to target

				if (Rz < -30) & (abs((target[ind])-PC1) >= 0.01):
					Rspeed = int(speed[speedind]*math.copysign(1,((target[ind])-PC1)))
					Lspeed = 0
				else:
					Rspeed = 0
					Lspeed = 0
					phase = 1
			elif (phase == 1): #wait for treadmill to stop
				if abs(SpdPak[1])<5 and  abs(SpdPak[2])<5:
					phase = 2
			elif (phase == 2):
				ind = ind+1
				if (ind>2):
					ind = 0
					speedind = speedind+1
				if (speedind>2): #finished
					phase = 3
				else:
					phase = 0
			elif (phase == 3):
				#done
				print('finished')
				Rspeed = 0
				Lspeed = 0
			#send speed update
			speedlist = [Rspeed,Lspeed,1400,1400,0]
			qq.put(speedlist)
			#save data
			savestring = [FN,Rz,Lz,phase,PC1,SpdPak[1],SpdPak[2]]#organize the data to be written to file			
			q3.put(savestring)

	cpps.kill()
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
			print('root',root)
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			q.put(root)#place the etree into the threading queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()

def sendtreadmillcommand(speedlist,qq,speedread,q4):
	
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
		
	def parsepacket(inpack):
		fmtin = struct.Struct('>B 5h 21B')
		try:
			treadsave = fmtin.unpack(inpack)
			return treadsave
		except:
			return['nan','nan','nan','nan','nan','nan']

	while not endflag.isSet():
		global old0
		global old1
		
		if (qq.empty()==False): #if there is a speed command to send...
		
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
			inpack = ''
			temp = s2.recv(1)
			s2.setblocking(False)
			while (len(temp)>0):
				try:
					s2.recv(1)
				except:
					break
			s2.setblocking(True)
			inpack = s2.recv(32) #bytes
			speedread = parsepacket(inpack)
#			print('speedread: ',speedread)
			q4.put(speedread)
			
		else: #if there is nothing new to send
			inpack = ''
			temp = s2.recv(1)
			s2.setblocking(False)
			while (len(temp)>0):
				try:
					s2.recv(1)
				except:
					break
			s2.setblocking(True)
			inpack = s2.recv(32) #bytes
			speedread = parsepacket(inpack)
			print('speedread: ',speedread)
			q4.put(speedread)
			
			
			
	#at the end make sure the treadmill is stopped
	out = serializepacket(0,0,500,500,0)
	s2.send(out)
	s2.close()
	
def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'TM_Delays_rev1.txt' # SAVE THE DATA FILES... AS A NAME THAT MAKES SENCE
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','phase','Position','RBS','LBS'])
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
		
#	print data
	return data

endflag = threading.Event()#an event to raise when we are ready to stop recording
def raisestop(sign):
	#the sign passed in doesn't do anything, I just didn't know how to make this work without passing something in...
	print("stop flag raised")
	endflag.set()
	t1.join(5)
	t2.join(5)
	t3.join(5)
	t4.join(5)
	viz.quit()

root = ''#empty string
savestring = ''
speedlist = array.array('i')
speedread = array.array('i')
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
q4 = Queue.Queue()#for communicating received treadmill belt speeds
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q)) #CPP server, relays info from Nexus
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq,savestring,q3,speedread,q4)) #The boss, updates VR display and synchs other threads
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq,speedread,q4)) #talks to the treadmill
t4 = threading.Thread(target=savedata,args=(savestring,q3)) #saves data
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
