""" Psychometric Curve Generation Function for a two choice task, Version 4, uses DK2 (?)

NO RELIANT ON RANDOM DRIFT ON THE TREADMILL

STEP LENGTH, NOT ALPHAS AND X

Experimental piloting only!!!

(Step 1) Subjects recieve feedback on the vertical force of each foot

(Step 2) A subject stands in a pre-step pose where alpha and X are defined. Then another one. (SOMEDAY: randomize speeds, randomize alpha and X, adaptive  staircase)

(Step 3) Subjects indicate wether movement A or B felt like their back leg was farther from their body.


#Use with V2P DK2 R2
cjs 1/31/2016
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
import vizact # CJS 12/13 in order to get key presses... I thinkq
import time # CJS 12/13 in order to get key presses... I thinkq
import random #CJS??? 1/25/2017

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

#set targets based on TM base behavior
global targetAl   #alpha values
targetAl =0.2
global targetAr
targetAr = 0.2

global targetXXl   # X values
targetXXl = 0.2
global targetXXr
targetXXr = 0.2

SL_L=.4952164
SL_R=.5062866
mean_SL=(SL_L+SL_R)/2

global AVGtargetSL   #Step Length values
#AVGtargetSL =0.4
AVGtargetSL =mean_SL*.8

global targetAmean
targetAmean = (targetAr+targetAl)/2

global targetXmean # X target, CJS 12/17/2016
targetXmean = (targetXXr+targetXXl)/2

global targettol
targettol = 0.0375

global reftime
reftime=time.time()

global messagewin
#messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)
#messagewin = viz.addText(str(0),pos=[0.05,targetXmean+0.2,0],scale=[0.05,0.05,0.05])
messagewin = viz.addText(str(0),pos=[-0.05,targetXmean-0.2,0],scale=[0.05,0.05,0.05])
messagewin.visible(0)

global messagephase
#messagephase = viz.addText(str(0),pos=[0.05,targetXmean-0.32,0],scale=[0.05,0.05,0.05])
messagephase = viz.addText(str(0),pos=[-.11,0.3,0],scale=[0.05,0.05,0.05])
messagephase.visible(0)

global prompt4TwoChoice
#prompt4TwoChoice = viz.addText('Which Leg had a longer X?',pos=[-0.2,0.4,0],scale=[0.05,0.05,0.05])
prompt4TwoChoice = viz.addText('Which step was Longer?',pos=[-.2,0.4,0],scale=[0.05,0.05,0.05])
prompt4TwoChoice.visible(0)

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =10
#setup array of randomly picked steps
global randy
randy = []
order = [1,2] * 5
while len(randy) < 1:#optimistically sample the solution space for test orders, reduced from 100 on 11/3/2015 to reduce calculation time for high stepnum
    random.shuffle(order)
    if order in randy:
        continue
    if all(len(list(group)) < 4 for _, group in itertools.groupby(order)):
        randy.append(order[:])
randy = [item for sublist in randy for item in sublist]
print(randy)

##############################CJS 12/13##############################
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

global PSYCHO
PSYCHO=0
###################################################################

global boxR
boxR = viz.addTexQuad(pos=[0.2,0,0],scale=[0.2,0.1,0])
boxR.color(0,0.7,1)
boxR.visible(0)

global boxL
boxL = viz.addTexQuad(pos=[-0.2,0,0],scale=[0.2,0.1,0])
boxL.color(0,0.7,1)
boxL.visible(0)

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

##setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0

global repeatcount
repeatcount = 0

global Rspeed
Rspeed = 0

global Lspeed
Lspeed = 0

global RHS
global LHS
RHS = 0
LHS = 0
global TargetXXX
TargetXXX=0
###################CJS 12/17/2016 ###########################
''' Setup order of distances to probe in sets'''
#ranTar=[0, .02, -.02, .06, -.06, .10, -.10] #CJS 12/17/2016
ranTar=[0,.01, -.01, .02, -.02,.03, -.03, .04, -.04, .06, -.06, .08, -.08] #CJS 1/16/2016
sets=1

global maxstep
maxstep = sets*len(ranTar)

global frodo
frodo = list()

for x in range(1,sets+1, 1):
	random.shuffle(ranTar)#mix up the order
	frodo = frodo+[ranTar[0]]
	frodo = frodo+[ranTar[1]]
	frodo = frodo+[ranTar[2]]
	frodo = frodo+[ranTar[3]]
	frodo = frodo+[ranTar[4]]
	frodo = frodo+[ranTar[5]]
	frodo = frodo+[ranTar[6]]
	frodo = frodo+[ranTar[7]]
	frodo = frodo+[ranTar[8]]
	frodo = frodo+[ranTar[9]]
	frodo = frodo+[ranTar[10]]
	frodo = frodo+[ranTar[11]]
	frodo = frodo+[ranTar[12]]


global Samwise1
Samwise1= list()

global Samwise2
Samwise2= list()

for x in range(1,sets+1, 1):
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	Samwise1=Samwise1+[random.randrange(250, 350, 10)]
	
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]
	Samwise2=Samwise2+[random.randrange(250, 350, 10)]

############################################################

global phaxxe
phaxxe = 0 #don't start at match ankles because there is no previous test to look at, indexing error in stepind

#experimental, add lines where alpha and X should be

#alphal = vizshape.addBox(size=[1,0.002,0.001])
#alphal.setPosition(0,targetUr,0)
#Xl = vizshape.addBox(size=[1,0.002,0.001])
#Xl.setPosition(0,targetXr,0)

#create latitudinal grid, "10" is the target step length, the grid expands above and belo
#lines = {}#create empty dictionary
#for x in range(1,12,1):
#	lines["Tp{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
#	lines["Tp{0}".format(x)].setPosition(0,targetmean+0.05*targetmean+(x-1)*0.1*targetmean,0)#each gap represents 20 percent of target?
#	lines["Tn{0}".format(x)]=vizshape.addBox(size=[1,0.002,0.001])
#	lines["Tn{0}".format(x)].setPosition(0,targetmean+0.05*targetmean-(x-1)*0.1*targetmean,0)
##	print((x-1)*0.02)
#global tnums
#tnums = {}
#for x in range(0,21,1):
#	if (x<10):
#		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[0,targetmean-0.95*targetmean-0.1*targetmean+x*0.1*targetmean+0.005,0],scale=[0.015,0.015,0.015])
#	else:
#		tnums["Num{0}".format(x)]=viz.addText(str(x),pos=[-0.005,targetmean-0.95*targetmean-0.1*targetmean+x*0.1*targetmean+0.005,0],scale=[0.015,0.015,0.015])
#	
viz.MainView.setPosition(0,targetXmean+0.05, -0.57)
viz.MainView.setEuler(0,0,0)


#######################CJS 12/13/2016 #############################
global target
target = 0

global step
step=0

global plateau
plateau=0

global SpdPak
SpdPak=()

global speeder
speeder=0
##################################################################

def UpdateViz(root,q,speedlist,qq,savestring,q3,speedread,q4):
#	timeold = time.time()

	while not endflag.isSet():
		global cursorR
		global cursorL
		global target
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
		global RHS
		global LHS
		global target
		global frodo
		global step
		global PSYCHO
		global targetAmean
		global targetXmean # X target, CJS 12/17/2016
		global messagephase
		global prompt4TwoChoice
		global TargetXXX
		global AVGtargetSL 
		global plateau
		global reftime
		global maxstep
		global SpdPak
		global Samwise1
		global Samwise2
		global speeder
		
		if (q4.empty()==False) :
			SpdPak=q4.get()#1 is the right belt speed, 2 is the left belt speed; the treadmill comunicates in mm/s!
			#print('Length q4: ', q4.qsize() ,' RBS: ',SpdPak[1], 'LBS: ',SpdPak[2])
		
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
#			RGT = float(data["RGT"][1])/1000
#			LGT = float(data["LGT"][1])/1000
			Rgamma = LANKY-RANKY
			Lgamma = RANKY-LANKY
#			Ralpha = (LGT+RGT)/2-RANKY
#			Lalpha = (LGT+RGT)/2-LANKY
#			Rx = RANKY-(LGT+RGT)/2
#			Lx = LANKY-(LGT+RGT)/2
			
			################CJS 12/13/2016 #################
			''' This shows force feedback, bars will turn green when within 10% of evenly distrutued'''
			cursorR.visible(1)
			cursorL.visible(1)
#			cursorR.setScale(0.2,(-Rz/1000),0.001)
#			cursorL.setScale(0.2,(-Lz/1000),0.001)
			cursorR.setScale(0.15,(-Rz/1000),0.001)
			cursorL.setScale(0.15,(-Lz/1000),0.001)
			if (abs(Rz -Lz)<(Rz*-.1)) & (abs(Rz -Lz)<(Lz*-.1)):
				cursorR.color(viz.GREEN)
				cursorL.color(viz.GREEN)
			else:
				#print (abs(Rz -Lz), '~<', (Rz*.1), 'or', (Lz*.1))
				cursorR.color(0.5,0.5,0.5)
				cursorL.color(0.5,0.5,0.5)
			#########################################


			################CJS 1/6/2017 #################
			''' This is going to cycle through a single trial where the following happens:
			(1) The reference configuration, on the reference leg is made and held for two seconds
			(2) Simulated step:
			(2A) The random frodo target is distance is given on the target leg
			(2B) SUBJECT ARE PROMPTED FOR which was longer'''
			if (Rz < -30) & (Lz < -30):
				if (step==0): # TRIAL IS STARTING, THIS IS TO MAKE SURE THE BELTS DON'T MOVE UNTIL ALL DATA IS READING
					speeder=0
					#startreftime=time.time()
					desiredSL=0
					targetSL=0
					phaxxe==5
					if (time.time()-reftime>=5):
						step=1
				elif (step==1): # reference step, for now assuming the right leg is the reference X	
				#if (step==1): # reference step, for now assuming the right leg is the reference X
					messagephase.visible(1)
					speeder=Samwise1[stepind]
					#print("Reference, Right=0")					
					#messagephase.message('Reference')			
					prompt4TwoChoice.visible(0)
					desiredSL=Rgamma
					targetSL=AVGtargetSL 
					RIGHT=1;
					if phaxxe==5:
						messagephase.message('Reference')	
						plateau=1;
						if (abs(Rz -Lz)<(Rz*-.1)) & (abs(Rz -Lz)<(Lz*-.1)):
							#print("Step 1: Elapsed time: ", time.time()-reftime)
							if (time.time()-reftime>=10):
								step=step+1
								desiredSL=Lgamma
#								if (stepind==maxstep):
#									#targetSL=AVGtargetSL-frodo[stepind-1]
#									phaxxe=4
#								else:
#									phaxxe=0
								phaxxe=0
								RIGHT=0;
								plateau=0
								messagephase.message('')
				elif (step==2): #test step, for now assuming the leg leg is the target X
					messagephase.visible(1)
					speeder=Samwise2[stepind]
					#print("Test, Right=1")					
					#messagephase.message('Test')
					desiredSL=Lgamma 
					if (stepind==maxstep):
						targetSL=AVGtargetSL-frodo[stepind-1]
					else:
						targetSL=AVGtargetSL-frodo[stepind]
					RIGHT=0;
					if (phaxxe==5):#PSYCHO
						messagephase.message('Test')
						plateau=1;
						if (abs(Rz -Lz)<(Rz*-.1)) & (abs(Rz -Lz)<(Lz*-.1)):
							#reftime = time.time()
							#prompt4TwoChoice = viz.addText('Which Leg had a longer X?',pos=[0,0.4,0],scale=[0.05,0.05,0.05])
							prompt4TwoChoice.visible(1)
							#print("Step 2: Elapsed time: ", time.time()-reftime)
							if (PSYCHO!=0) or (time.time()-reftime>=20):
								
								prompt4TwoChoice.visible(0)
								#time.sleep(10)	# Wait for 5 seconds
								step=step+1
								#print('@@@@@@@@@@@ Stepind :', stepind, ' MAX STEP: ', maxstep)
								if (stepind==maxstep-1):#was -1
									#targetSL=AVGtargetSL-frodo[stepind-1]
									phaxxe=4
								else:
									phaxxe=0
								step=1	
								stepind=stepind+1	
								desiredSL=Rgamma
								targetSL=AVGtargetSL 
								RIGHT=1;
								plateau=0;
								messagephase.message('')
				else:
					print('Warning phase value un-defined')
			else:
				if (stepind==maxstep):
					phaxxe=4
				else:
					print('Warning how on earth did you end up here?')
					desiredSL=AVGtargetSL 
					targetSL=AVGtargetSL-frodo[stepind]
			
						#adjust alpha on right leg
			print ("****************** Trial: ", stepind, " step: ", step, " phase: ", phaxxe, " SL of interst: ",  desiredSL,  " TargetSL: ", targetSL, " PSYCHO: ", PSYCHO, " RBelt Speed:  ", Rspeed, " LBelt Speed:  ", Lspeed, "   ******************")
			if (phaxxe == 0)and (step!=0):
				#messagewin.message(str(phaxxe))
				print ("RANKY: ", (RANKY), " LANKY: ", (LANKY))
#				if (Rz < -30) & (Lz < -30) & ((1.1<RANKY) or (1.1<LANKY)): #this is to make sure that people more or less stay in the middle of the treadmill
#					print ("1.1 < ", (RANKY), "OR  1.1 < ", (LANKY))
#					Lspeed = int(300*math.copysign(1,-1*((LANKY)-(1.1))))
#					Rspeed = int(300*math.copysign(1,-1*((RANKY)-(1.1))))
#				elif (Rz < -30) & (Lz < -30) & ((RANKY<0.5) or (LANKY<0.5)): #this is to make sure that people more or less stay in the middle of the treadmill
#					print ((RANKY), "<0.5 OR ", (LANKY), "<0.5qq" )
#					Lspeed = int(300*math.copysign(1,1*((.5)-(LANKY))))
#					Rspeed = int(300*math.copysign(1,1*((.5)-(RANKY))))
				if (Rz < -30) & (Lz < -30) & ((1.5<RANKY)):
					print ("1.5 < ", (RANKY))
					Lspeed = int(100*math.copysign(1,-1*((RANKY)-(1.5))))
					Rspeed = int(100*math.copysign(1,-1*((RANKY)-(1.5))))
				elif (Rz < -30) & (Lz < -30)& (1.5<LANKY): #this is to make sure that people more or less stay in the middle of the treadmill
					print ("1.5 < ", (LANKY))
					Lspeed = int(100*math.copysign(1,-1*((LANKY)-(1.5))))
					Rspeed = int(100*math.copysign(1,-1*((LANKY)-(1.5))))
				elif (Rz < -30) & (Lz < -30) & ((RANKY<0.5)): #this is to make sure that people more or less stay in the middle of the treadmill
					print ((RANKY), "<0.5" )
					Lspeed = int(100*math.copysign(1,1*((.5)-(RANKY))))
					Rspeed = int(100*math.copysign(1,1*((.5)-(RANKY))))
				elif (Rz < -30) & (Lz < -30) & ((LANKY<0.5)): #this is to make sure that people more or less stay in the middle of the treadmill
					print ((LANKY), "<0.5" )
					Lspeed = int(100*math.copysign(1,1*((.5)-(LANKY))))
					Rspeed =  int(100*math.copysign(1,1*((.5)-(LANKY))))
				#elif (Rz < -30) & (Lz < -30) & ((1.1>RANKY>0.5) or (1.1>LANKY>0.5)): #this is to make sure that people more or less stay in the middle of the treadmill
				elif (Rz < -30) & (Lz < -30) & ((1.5>RANKY)) & (1.5>LANKY) & ((RANKY>0.5)) & ((LANKY>0.5)): #this is to make sure that people more or less stay in the middle of the treadmill
					Rspeed = 0
					Lspeed = 0
					phaxxe = 1
				else:
					Rspeed = 0
					Lspeed = 0
			elif (phaxxe == 1) and (step!=0) :
				#messagewin.message(str(phaxxe))
				if (Rz < -30) & (Lz < -30) & (abs((targetSL)-(desiredSL)) >= 0.14)  : #Undershot the target outside the tolerance of 0.04
					#print ("A. AlphaDiff: ", (targetALPHA-desiredALPHA), " XDiff: ", (targetXXX-desiredX), " RightFirst: ", RIGHT)
					if RIGHT==0:
#						Lspeed = int(300*math.copysign(1,-1*((targetSL)-(desiredSL))))
#						Rspeed = int(300*math.copysign(1,((targetSL)-(desiredSL))))
						Lspeed = int(speeder*math.copysign(1,-1*((targetSL)-(desiredSL))))
						Rspeed = int(speeder*math.copysign(1,((targetSL)-(desiredSL))))
					elif RIGHT==1:
#						Rspeed = int(300*math.copysign(1,-1*((targetSL)-(desiredSL))))
#						Lspeed = int(300*math.copysign(1,((targetSL)-(desiredSL))))
						Rspeed = int(speeder*math.copysign(1,-1*((targetSL)-(desiredSL))))
						Lspeed = int(speeder*math.copysign(1,((targetSL)-(desiredSL))))
				elif (Rz < -30) & (Lz < -30) &(abs((targetSL)-(desiredSL)) < 0.14): #Within the target tolerance of 0.04
					Rspeed = 0
					Lspeed = 0
					phaxxe = 2
				else:
					Rspeed = 0
					Lspeed = 0
			elif (phaxxe == 2) and (step!=0) :  #We wait to get a readinf from the readmill indicating that the belts have come to a stop
				#time.sleep(2)
				#messagewin.message(str(phaxxe))
#				if (q4.empty()==False) : #if there is something in q4, i.e., a recent packet from the treadmill :)
#					SpdPak=q4.get()#1 is the right belt speed, 2 is the left belt speed; the treadmill comunicates in mm/s!
#					print('Length q4: ', q4.qsize() ,' RBS: ',SpdPak[1], 'LBS: ',SpdPak[2])
				if abs(SpdPak[1])<5 and  abs(SpdPak[2])<5:
					Rspeed = 0
					Lspeed = 0
					phaxxe = 3
				else:
					Rspeed = 0
					Lspeed = 0
			
			elif (phaxxe == 3) and (step!=0) : #Only move one belt so that we can be more accuate
				#messagewin.message(str(phaxxe))
				if (Rz < -30) & (Lz < -30) & (abs(targetSL-desiredSL) >= 0.01)  : #Undershot the target outside the tolerance of 0.04
					if RIGHT==0:
						Lspeed = int(50*math.copysign(1,-1*(targetSL-desiredSL)))
					elif RIGHT==1:
						#Rspeed = int(50*math.copysign(1,-1*(targetSL-desiredSL)))
						Lspeed = int(50*math.copysign(1,(targetSL-desiredSL)))
				elif (Rz < -30) & (Lz < -30) &(abs(targetSL-desiredSL) < 0.01): #Within the target tolerance of 0.01
					Rspeed = 0
					Lspeed = 0
					reftime = time.time()
					if (stepind-1==maxstep):
						phaxxe = 4
					else:
						phaxxe = 5
						plateau=1;
				else:
					Rspeed = 0
					Lspeed = 0	
			elif (phaxxe == 4) and (step!=0) :#end of trial move the feet together
				messagewin.message('Test Complete!')
				messagewin.visible(1)
				plateau=1;
				Rspeed = 0
				Lspeed = 0
			elif (phaxxe == 5) or  (step==0) :#end of trial move the feet together
				Rspeed = 0
				Lspeed = 0
			else:
				messagewin.message('Test Complete!')
				print('Warning phase value un-defined')
				print(" LeftBeltSpeed: ", Lspeed, " RightBeltSpeed: ", Rspeed)
				Rspeed = 0
				Lspeed = 0	
				
			#send speed update
			
			speedlist = [Rspeed,Lspeed,1300,1300,0]#the accelerations "1200 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
			qq.put(speedlist)

			histzR = Rz
			histzL = Lz
			#save data
			#if ((stepind)!=(maxstep)):
			#if ((stepind)<(maxstep)):
#				print('$$$$$$$$  FRODO: ', frodo, ' INDEX : ', stepind, ' MAX STEP: ', maxstep, ' THIS SHOULD WORK? :', frodo[stepind])
#				savestring = [FN,Rz,Lz,RHS,LHS,RANKY-LANKY,LANKY-RANKY,RANKY,LANKY,PSYCHO, frodo[stepind], time.time(), stepind, step, phaxxe, desiredSL, targetSL, plateau, AVGtargetSL, reftime, speeder]#organize the data to be written to file			
			
			if ((stepind)==(maxstep)):
				savestring = [FN,Rz,Lz,RHS,LHS,RANKY-LANKY,LANKY-RANKY,RANKY,LANKY,PSYCHO, frodo[stepind-1], time.time(), stepind, step, phaxxe, desiredSL, targetSL, plateau, AVGtargetSL, reftime, speeder, Rspeed, Lspeed]#organize the data to be written to file	
			else:
				savestring = [FN,Rz,Lz,RHS,LHS,RANKY-LANKY,LANKY-RANKY,RANKY,LANKY,PSYCHO, frodo[stepind], time.time(), stepind, step, phaxxe, desiredSL, targetSL, plateau, AVGtargetSL, reftime, speeder, Rspeed, Lspeed]#organize the data to be written to file	

			
			#print('$$$$$$$$ Stepind :', stepind, ' MAX STEP: ', maxstep)
			q3.put(savestring)

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
			#print('speedread: ',speedread)
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
			#print('speedread: ',speedread)
			q4.put(speedread)
			
			
			
	#at the end make sure the treadmill is stopped
	out = serializepacket(0,0,500,500,0)
	s2.send(out)
	s2.close()
	
def savedata(savestring,q3):
	
	#initialize the file
	mst = time.time()
	mst2 = int(round(mst))
	mststring = str(mst2)+'PSYCHO_X_TwoChoice_V4.txt' # SAVE THE DATA FILES... AS A NAME THAT MAKES SENCE
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','rgamma','lgamma','RANK','LANK', 'PSYCHO', 'frodo', 'time', 'stepind', 'step', 'phaxxe', 'desiredSL', 'targetSL','plateau', 'AVGtargetSL', 'reftime', 'Speeder',"Rspeed", "Lspeed"])
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

def TargetUpdate(arg):
	global target
	target=target+.05
	
def KepPressDetector(arg):
	global PSYCHO
	PSYCHO=arg
	prompt4TwoChoice.visible(0)


vizact.onkeydown('q',raisestop,'biggle')#biggle is meaningless, just need to pass something into the raisestop callback
###################### CJS 12/17/2016 ###################### 
''' This will take the ibnput from the Logitech to indicate if the first or the second trial was longer'''
vizact.onkeydown('65366',KepPressDetector, 1) # Second trial was longer
vizact.onkeyup('65366',KepPressDetector, 0) #No longer indicating anything
vizact.onkeydown('65365',KepPressDetector, -1) # First trial was longer
vizact.onkeyup('65365',KepPressDetector, 0) #No longer indicating anything
print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
print('^^^^^^^^^^^^^^^^^^Key Press^^^^^^^^^^^^^^')
print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
############################################################ 