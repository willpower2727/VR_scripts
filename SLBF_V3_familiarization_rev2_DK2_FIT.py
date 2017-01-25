""" Step Length Biofeedback familiarization task, Version 3, uses DK2

A subject stands in a neutral position with feet placed together. On que, subject takes two steps forward with target step lengths

Biofeedback is shown as a grid display as in Vazquez et al 2015. Subjects are shown their ANK-ANK distance @ HS

#Use with V2P DK2 R2
wda 10/28/2016

Rev 2 adds fine-tuned adjustments to pre-step ankle positions. Ankles must be within 1 cm of eachother before starting
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
import vizlens
import oculus
import subprocess
import vizfx

global cpps
cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe"')
time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
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


global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor()
#profile = hmd.getProfile()
#hmd.setIPD(profile.ipd)

#set targets based on TM base behavior
global targetUl
targetUl =0.5369
global targetUr
targetUr = 0.5369

global targetmean
targetmean = (targetUr+targetUl)/2

global targettol
targettol = 0.01

global messagewin
#messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)
messagewin = viz.addText(str(0),pos=[0.05,targetmean+0.2,0],scale=[0.05,0.05,0.05])

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =80  #80 sets of steps
#setup array of randomly picked steps
global randy
randy = []
order = [1,2] * 5
print('Calculating random step orders...')
while (len(randy) < 8):#optimistically sample for test orders (r or l first)
    random.shuffle(order)
    if order in randy:
        continue
    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
        randy.append(order[:])
randy = [item for sublist in randy for item in sublist]
print(randy)
#randy = random.choice(randy)#order of tests, pseudo random. No more than 3 same sided tests in a row
#print(randy)

global circleL #slow leg circle marker
circleL = vizshape.addSphere(0.01,50,50,color=viz.GREEN)
circleL.setPosition(-0.03,targetmean,0)
circleL.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global circleR #slow leg circle marker
circleR = vizshape.addSphere(0.01,50,50)
circleR.color(1,0.7,0)
circleR.setPosition(0.04,targetmean,0)
circleR.disable(viz.LIGHTING)#no shading, we don't want depth perception here

global highlightr
highlightr = vizshape.addBox(size=[0.25,0.0175,0.001])
highlightr.color(0,0,1)
highlightr.setPosition(0.145,targetmean,0)
highlightr.disable(viz.LIGHTING)
#highlightr.visible(0)

global highlightl
highlightl = vizshape.addBox(size=[0.25,0.0175,0.001])
highlightl.color(0,0,1)
highlightl.setPosition(-0.135,targetmean,0)
highlightl.disable(viz.LIGHTING)

##setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0

global stepind #this keeps track of the total # of attempts
stepind = 0

global histzR
histzR = 0
global histzL
histzL = 0

global steplengthL
steplengthL = 0
global steplengthR
steplengthR = 0

global Rattempts
Rattempts = 0
global Lattempts
Lattempts = 0

global old0
old0 = 0
global old1
old1 = 0

global rgorb
global lgorb
rgorb = 0
lgorb = 0

global rbad
global lbad
rbad = 0
lbad = 0

global repeatcount
repeatcount = 0

global Rspeed
global Lspeed
Rspeed = 0
Lspeed = 0

global RHSflag #use these to designate when 2 events have occured
global LHSflag
RHSflag = 0
LHSflag = 0

#setup order of highlights
short = -0.06
long = 0.06
med = 0
global frodo
frodo = list()

global samwise
samwise = list()
#create pseudo randomized sets of 3
#randy2 = [short,med,long]
randy2 = [short,long]

for x in range(1,3,1):
#	random.shuffle(randy2)#mix up the order #no random possible with 2 targets
#	print(randy2)
	frodo = frodo+[randy2[0]]*20
	frodo = frodo+[randy2[1]]*20
#	frodo = frodo+[randy2[2]]*50
	
#	samwise = samwise+[1]*25
#	samwise = samwise+[0]*25
#	samwise = samwise+[1]*25
#	samwise = samwise+[0]*25
#	samwise = samwise+[1]*25
#	samwise = samwise+[0]*25

print('frodo: ',len(frodo) )

global phaxxe
phaxxe = 1 #don't start at match ankles because there is no previous test to look at, indexing error in stepind

#create latitudinal grid, "10" is the target step length, the grid expands above and belo
lines = {}#create empty dictionary
for x in range(1,12,1):
	lines["Tp{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
	lines["Tp{0}".format(x)].setPosition(0,targetmean+0.01+(x-1)*0.02,0)
	lines["Tn{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
	lines["Tn{0}".format(x)].setPosition(0,targetmean+0.01-(x-1)*0.02,0)
#	print((x-1)*0.02)
global tnums
tnums = {}
for x in range(0,21,1):
	if (x<10):
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,targetmean-0.2-0.01+x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	else:
		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,targetmean-0.2-0.01+x*0.02+0.005,0],scale=[0.015,0.015,0.015])
	
viz.MainView.setPosition(0,targetmean+0.05, -0.57)
viz.MainView.setEuler(0,0,0)

def UpdateViz(root,q,speedlist,qq,savestring,q3):
#	timeold = time.time()

	while not endflag.isSet():
		global circleL
		global circleR
		global histzL
		global histzR
		global STEPNUM
		global Rattempts
		global Lattempts
		global stepind
		global randy
		global rgorb
		global lgorb
		global Rspeed
		global Lspeed
		global phaxxe
		global messagewin
		global rbad
		global lbad
		global RCOUNT
		global LCOUNT
		global RHSflag
		global LHSflag
		
		
		root = q.get()#look for the next frame data in the thread queue
		if root is None:
			continue
		else:
			data = ParseRoot(root)
			FN = int(data["FN"])
			Rz = float(data["Rz"])
			Lz = float(data["Lz"])
			#look for marker data

			RANKY = float(data["RANK"][1])/1000
			LANKY = float(data["LANK"][1])/1000

			Rgamma = LANKY-RANKY
			Lgamma = RANKY-LANKY
			
			#state machine
			if (phaxxe == 0):  #move farthest foot first
				if (stepind>=STEPNUM):
					phaxxe = 5
					continue
				try:
#					if (randy[stepind-1] == 1) & (randy[stepind] == 1):#previously a right step next is also right
#						phaxxe = 1 #proceed
					if (randy[stepind-1] == 2):# & (randy[stepind] == 2): #need to match ankles first!
						#move right ankle to left ankle
						if (Rz < -30) & (Lz < -30) &(abs(1.5-RANKY) >= 0.04):
							Rspeed = int(300*math.copysign(1,1.5-RANKY))
						elif (Rz < -30) & (Lz < -30) &(abs(1.5-RANKY) < 0.04):
							Rspeed = 0
							phaxxe = 1
						else:
							Rspeed = 0
					elif (randy[stepind-1] == 1):# & (randy[stepind] == 1): #need to match ankles first
						if (Rz < -30) & (Lz < -30) & (abs(1.5-LANKY) >= 0.04):
							Lspeed = int(300*math.copysign(1,1.5-LANKY)) 
						elif (Rz < -30) & (Lz < -30) & (abs(1.5-LANKY) < 0.04):
							Lspeed = 0
							phaxxe = 1
						else:
							Lspeed = 0
#					elif (randy[stepind-1] == 2) & (randy[stepind] == 2):
#						phaxxe = 1#proceed
					messagewin.message('Moving...')
					messagewin.visible(1)
				except:
#					if (stepind >= STEPNUM):
					if (stepind >= STEPNUM): #stop if we run out of tests
						disp('Max # of steps reached')
						phaxxe = 5
						messagewin.message('Test Complete!')
						messagewin.visible(1)
						print('max steps reached')
					
			#phase 1 move right leg to position
			elif (phaxxe == 1):
				messagewin.message('Moving...')
				messagewin.visible(1)
				#move to the initial pose
				try:
					if (randy[stepind] == 1):#right leg next test
						if (Rz < -30) & (Lz < -30) & (abs(1.5-RANKY) >= 0.04):#right foot is not at 1.45 m from origin
							Rspeed = int(300*math.copysign(1,1.5-RANKY))
						else:
							Rspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs(1.5-RANKY) < 0.04):#everything is ready for the left leg to move next
							phaxxe = 2#proceed to move left leg

					elif (randy[stepind] == 2):#left leg next test
						if (Rz < -30) & (Lz < -30) & (abs(1.5-RANKY) >= 0.04):#right foot is not at start position (1.45-target)
							Rspeed = int(300*math.copysign(1,1.5-RANKY))
						else:
							Rspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs(1.5-RANKY) < 0.04):
							phaxxe = 2#proceed to move left leg

				except:
#					if (stepind >= STEPNUM):
					if (stepind >= STEPNUM): #stop if we run out of tests
						disp('Max # of steps reached')
						phaxxe = 5
					
			#phase 2 move left foot
			elif (phaxxe == 2):
				messagewin.message('Moving...')
				messagewin.visible(1)
				try:
					if (randy[stepind] == 1):#right leg next test
						if (Rz < -30) & (Lz < -30) & (abs(1.5-LANKY) >= 0.04):#left foot is not at start position (1.45-target)
							Lspeed = int(300*math.copysign(1,1.5-LANKY))
						else:
							Lspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs(1.5-LANKY) < 0.04):#everything is ready for the next step so display next target
							phaxxe = 2.5 #proceed to prep pose

					elif (randy[stepind] == 2):#left leg next test
						if (Rz < -30) & (Lz < -30) & (abs(1.5-LANKY) >= 0.04):#left foot is not at 1.45 m from origin
							Lspeed = int(300*math.copysign(1,1.5-LANKY))
						else:
							Lspeed = 0
						if (Rspeed == 0) & (Lspeed == 0) & (abs(1.5-LANKY) < 0.04):#everything is ready for the next step so display next target
							phaxxe = 2.5
				except:
#					if (stepind >= STEPNUM):
					if (stepind >= STEPNUM): #stop if we run out of tests
						disp('Max # of steps reached')
						phaxxe = 5
#					Rspeed = 0
#					Lspeed = 0
					boxR.visible(0)
					boxL.visible(0)
					
			elif(phaxxe == 2.5): #closely match the feet together
				messagewin.message('Adjusting Left...')
				messagewin.visible(1)
				
				try:#adjust Left leg
					if (Rz < -30) & (Lz < -30) & (abs(1.5-LANKY) >= 0.005):#left foot is not at start position (1.45-target)
						Lspeed = int(50*math.copysign(1,1.5-LANKY))
					else:
						Lspeed = 0
					if (Rspeed == 0) & (Lspeed == 0) & (abs(1.5-LANKY) < 0.005):#everything is ready for the next step so display next target
							phaxxe = 2.6 #proceed to prep pose
				except:
#					if (stepind >= STEPNUM):
					if (stepind >= STEPNUM): #stop if we run out of tests
						disp('Max # of steps reached')
						phaxxe = 5
#					Rspeed = 0
#					Lspeed = 0
#					boxR.visible(0)
#					boxL.visible(0)
					
			elif(phaxxe == 2.6):
				messagewin.message('Adjusting Right...')
#				try: #adjust right leg
				if (Rz < -30) & (Lz < -30) & (abs(1.5-RANKY) >= 0.005):#left foot is not at start position (1.45-target)
					Rspeed = int(50*math.copysign(1,1.5-RANKY))
				else:
					Rspeed = 0
				if (Rspeed == 0) & (Lspeed == 0) & (abs(1.5-RANKY) < 0.005):#everything is ready for the next step so display next target
						phaxxe = 3 #proceed to prep pose
#				except:
#					if (stepind >= STEPNUM):
				if (stepind >= STEPNUM): #stop if we run out of tests
					disp('Max # of steps reached')
					phaxxe = 5
#					Rspeed = 0
#					Lspeed = 0
#				boxR.visible(0)
#				boxL.visible(0)
			
			#phase 3 pre-pose
			elif (phaxxe == 3):
#				viz.visible(0)#turn off display
				try:
					if (randy[stepind] == 1):#right leg next test
						highlightr.visible(1)
						highlightl.visible(0)
						highlightr.setPosition(0.145,targetmean+frodo[stepind],0)
						messagewin.visible(0)
						phaxxe = 4#proceed with test
						
					elif (randy[stepind] == 2):#left leg next test
						highlightr.visible(0)
						highlightl.visible(1)
						highlightl.setPosition(-0.135,targetmean+frodo[stepind],0)
						messagewin.visible(0)
						phaxxe = 4
							
				except:
#					if (stepind >= STEPNUM):
					if (stepind >= STEPNUM): #stop if we run out of tests
						print('Max # of steps reached')
						phaxxe = 5
					else:
						print('Unknown error in phase 3, stopping...')
						phaxxe = 5
			
			#phase 4 attempt
			elif (phaxxe == 4):
				messagewin.visible(0)
					
				if (Rz <= -30) & (histzR > -30):#RHS condition
					RHSflag = 1
#					stepind = stepind+1
					Rattempts = Rattempts+1
#					cursorR.visible(0)#turn off the cursor
					circleR.setPosition(0.05,Rgamma,0)
					if (abs((LANKY-RANKY)-targetUr) <= targettol):
						RCOUNT = RCOUNT+1
						rbad = 0
						rgorb = 1
					else:
						rbad = rbad+1
						rgorb = 0
#					rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
#					phaxxe = 0
					
				
				if (Lz <= -30) & (histzL > -30):#LHS condition
					LHSflag = 1
#					stepind = stepind+1
					Lattempts = Lattempts+1
#					cursorL.visible(0)
					circleL.setPosition(-0.05,Lgamma,0)
					if (abs((RANKY-LANKY)-targetUl) <= targettol):
						LCOUNT = LCOUNT+1
						lbad = 0
						lgorb = 1
					else:
						lbad = lbad +1
						lgorb = 0
#					leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
#					phaxxe = 0
					
				if (RCOUNT >= STEPNUM) & (LCOUNT >= STEPNUM):
					phaxxe = 5
				elif (rbad >= 20) | (lbad >=20):
#					phaxxe = 5
					print "Too many bad steps in a row, take a break"
					
				if (RHSflag == 1) & (LHSflag == 1):
					stepind = stepind+1
					print stepind
					phaxxe = 0
					RHSflag = 0
					LHSflag = 0
					
					
					
			elif (phaxxe == 5):#end of trial move the feet together
				messagewin.message('Test Complete!')
				messagewin.visible(1)
				if (RANKY-LANKY >= 0.04) & (Rz < -30) & (Lz < -30):
					Lspeed = int(300*math.copysign(1,(RANKY-LANKY)))
					Rspeed = 0
				elif (LANKY-RANKY >= 0.04) & (Rz < -30) & (Lz < -30):
					Rspeed = int(300*math.copysign(1,(LANKY-RANKY)))
					Lspeed = 0
				else:
					Rspeed = 0
					Lspeed = 0
			else:
				disp('Warning phase value un-defined')

				
			#send speed update
			speedlist = [Rspeed,Lspeed,1350,1350,0]#the accelerations "1200 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
			qq.put(speedlist)
			
			histzR = Rz
			histzL = Lz
			#save data
			savestring = [FN,Rz,Lz,rgorb,lgorb,RANKY-LANKY,LANKY-RANKY,targetUr-(LANKY-RANKY),targetUl-(RANKY-LANKY),RANKY,LANKY,phaxxe,frodo[stepind]]#organize the data to be written to file
			q3.put(savestring)
#			timeold = time.time()
	cpps.kill()
#	q3.join()
	#print stats
	print('R',RCOUNT,'/',Rattempts)
	print('L',LCOUNT,'/',Lattempts)
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
#			print('root',root)
#			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
			q.put(root)#place the etree into the threading queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()

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
	
def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'SLBF_V3_Fam_rev1_DK2.txt'
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','rgorb','lgorb','rgamma','lgamma','rerror','lerror','RANK','LANK','phase','target'])
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
q = Queue.Queue()#initialize the queue
qq = Queue.Queue()#another queue for treadmill commands
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,speedlist,qq,savestring,q3))
t3 = threading.Thread(target=sendtreadmillcommand,args=(speedlist,qq))
t4 = threading.Thread(target=savedata,args=(savestring,q3))
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
	
