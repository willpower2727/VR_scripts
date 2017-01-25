""" Psychometric Curve Generation Function for a two choice task, Version 1, uses DK2 (?)

Experimental piloting only!!!

(Step 1) Subjects recieve feedback on the vertical force of each foot

(Step 2) A subject stands in a pre-step pose where alpha and X are defined. Then another one. (SOMEDAY: randomize speeds, randomize alpha and X, adaptive  staircase)

(Step 3) Subjects indicate wether movement A or B felt like their back leg was farther from their body.


#Use with V2P DK2 R2
cjs 12/13/2016
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

global targetAmean
targetAmean = (targetAr+targetAl)/2

global targetXmean # X target, CJS 12/17/2016
targetXmean = (targetXXr+targetXXl)/2

global targettol
targettol = 0.0375

global messagewin
#messagewin = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER_TOP,fontSize=60,icon=False,key=None)
messagewin = viz.addText(str(0),pos=[0.05,targetXmean+0.2,0],scale=[0.05,0.05,0.05])

global messagephase
messagephase = viz.addText(str(0),pos=[0.05,targetXmean-0.32,0],scale=[0.05,0.05,0.05])

global prompt4TwoChoice
prompt4TwoChoice = viz.addText('Which Leg had a longer X?',pos=[-0.2,0.4,0],scale=[0.05,0.05,0.05])
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

global boxL
boxL = viz.addTexQuad(pos=[-0.2,0,0],scale=[0.2,0.1,0])
boxL.color(0,0.7,1)

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
global Lspeed
Rspeed = 0
Lspeed = 0

global RHS
global LHS
RHS = 0
LHS = 0
global TargetXXX
TargetXXX=0
###################CJS 12/17/2016 ###########################
''' Setup order of distances to probe in sets'''
ranTar=[0, .02, -.02, .06, -.06, .10, -.10] #CJS 12/17/2016
sets=4

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
step=1
##################################################################

def UpdateViz(root,q,speedlist,qq,savestring,q3):
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
			RGT = float(data["RGT"][1])/1000
			LGT = float(data["LGT"][1])/1000
			Rgamma = LANKY-RANKY
			Lgamma = RANKY-LANKY
			Ralpha = (LGT+RGT)/2-RANKY
			Lalpha = (LGT+RGT)/2-LANKY
			Rx = RANKY-(LGT+RGT)/2
			Lx = LANKY-(LGT+RGT)/2
			
#			boxR.setScale(0.2,Ralpha,0)
#			boxL.setScale(0.2,Lx,0)

			################CJS 12/13/2016 #################
			''' This shows force feedback, bars will turn green when within 10% of evenly distrutued'''
			cursorR.visible(1)
			cursorL.visible(1)
			cursorR.setScale(0.2,(-Rz/1000),0.001)
			cursorL.setScale(0.2,(-Lz/1000),0.001)
			if (abs(Rz -Lz)<(Rz*-.1)) & (abs(Rz -Lz)<(Lz*-.1)):
				cursorR.color(viz.GREEN)
				cursorL.color(viz.GREEN)
			else:
				#print (abs(Rz -Lz), '~<', (Rz*.1), 'or', (Lz*.1))
				cursorR.color(0.5,0.5,0.5)
				cursorL.color(0.5,0.5,0.5)
			#########################################
			
#			################CJS 12/13/2016 #################
#			''' This is going to cycle through a single trial where the following happens:
#			(1) The trial starts with the feet together
#			(2) The reference configuration is made and held for a two seconds
#			(3) The feet are brought back together
#			(4A) The random frodo target is distance is given
#			(4B) SUBJECT ARE PROMPTED FOR which was longer
#			(5) The trial ends with the feet together '''
#			
#			if (step==1) or (step==3) or (step==5): # Bring the feet together
#				targetUR=0
#				targetXl=0
#				step=step+1;
#			elif (step==2): # reference step
#				targetUR=targetAr
#				targetXl=targetXXl
#				step=step+1;
#			elif (step==4): #test step
#				targetUR=targetAr
#				targetXl=frodo[stepind]
#				prompt4Psycho = viz.addText(str(rscore),pos=[-.6,0.4,0],scale=[0.1,0.1,0.1])
#				prompt4Psycho.visible(1)
#				prompt4Psycho.message('Press left if the first trial felt longer.  Press right is the second trial felt longer.')
#				step=0;
#			else:
#				disp('Warning phase value un-defined')
#			
#			#########################################
					
#			################CJS 12/20/2016 #################
#			''' This is going to cycle through a single trial where the following happens:
#			(1) The trial starts with the feet together
#			(2) The reference configuration, on the reference leg is made and held for two seconds
#			(3) Simulated step
#			(4A) The random frodo target is distance is given on the target leg
#			(4B) SUBJECT ARE PROMPTED FOR which was longer
#			(5) The trial ends with the feet together '''
#			#print("stepind: ",stepind," Step: ",step, " Phase: ", phaxxe)
#			if (Rz < -30) & (Lz < -30):
#				if (step==1) or (step==3) or (step==5): # Bring the feet together
#					print('LANKY: ', LANKY, ' RANKY: ', RANKY)
#					if LANKY<=RANKY:#(step==1) or (step==5):
#						print("LeftAnkle forward ")
##						desiredALPHA=LANKY
##						desiredX=LANKY
##						targetALPHA=RANKY
##						targetXXX=LANKY
#						desiredALPHA=.7
#						desiredX=LANKY
#						targetALPHA=RANKY
#						targetXXX=.7
#						RIGHT=1;
#						print("Right: ", 0)
#					elif LANKY>RANKY:#(step==3):
#						print("Rankle Forward ")
##						desiredALPHA=RANKY
##						desiredX=RANKY
##						targetALPHA=LANKY
##						targetXXX=RANKY
#						desiredALPHA=.7
#						desiredX=RANKY
#						targetALPHA=LANKY
#						targetXXX=.7
#						RIGHT=0;
#						print("Right: ", 0)
#					if (phaxxe==5):
##						reftime = time.time()
##						if (time.time()-reftime>=1):
#						#time.sleep(15)	# Wait for 5 seconds					
#						step=step+1
#						phaxxe=0
#				elif (step==2): # reference step, for now assuming the right leg is the reference X
#					#time.sleep(15)
#					desiredALPHA=Lalpha
#					desiredX=Rx
#					targetALPHA=targetAmean
#					targetXXX=targetXmean
#					RIGHT=0;
#					if phaxxe==5:
##						reftime = time.time()
##						if (time.time()-reftime>=10):
#						time.sleep(2.5)	# Wait for 5 seconds	
#						step=step+1
#						phaxxe=0
#				elif (step==4): #test step, for now assuming the leg leg is the target X
#					desiredALPHA=Ralpha
#					desiredX=Lx
#					targetALPHA=targetAmean
#					targetXXX=targetXmean-frodo[stepind]
#					RIGHT=1;
#					if (phaxxe==5):#PSYCHO
#						reftime = time.time()
#						prompt4TwoChoice = viz.addText('Which Leg had a longer X?',pos=[-.6,0.4,0],scale=[0.05,0.05,0.05])
#						prompt4TwoChoice.visible(1)
#						if (PSYCHO!=0) or (time.time()-reftime>=5):
#							prompt4TwoChoice.visible(0)
#							#time.sleep(10)	# Wait for 5 seconds
#							step=step+1
#							phaxxe=0
#							step=1		
#							stepind=stepind+1
#				else:
#					print('Warning phase value un-defined')
#			else:
#				desiredALPHA=Ralpha
#				desiredX=Lx
#				targetALPHA=0
#				targetXXX=0
#			#########################################
			################CJS 1/6/2017 #################
			''' This is going to cycle through a single trial where the following happens:
			(1) The reference configuration, on the reference leg is made and held for two seconds
			(2) Simulated step:
			(2A) The random frodo target is distance is given on the target leg
			(2B) SUBJECT ARE PROMPTED FOR which was longer'''
			if (Rz < -30) & (Lz < -30):
#				if (step==0): # Bring the feet together
#					#print('LANKY: ', LANKY, ' RANKY: ', RANKY)
#					if LANKY<=RANKY:#(step==1) or (step==5):
#						print("LeftAnkle forward ")
#						desiredALPHA=.7
#						desiredX=LANKY
#						targetALPHA=RANKY
#						targetXXX=.7
#						RIGHT=1;
#						print("Right: ", 0)
#					elif LANKY>RANKY:#(step==3):
#						print("Rankle Forward ")
#						desiredALPHA=.7
#						desiredX=RANKY
#						targetALPHA=LANKY
#						targetXXX=.7
#						RIGHT=0;
#						print("Right: ", 0)
#					if (phaxxe==5):				
#						step=step+1
#						phaxxe=0
				if (step==1): # reference step, for now assuming the right leg is the reference X
					print("Reference, Right=0")					
					messagephase.message('Reference')					
					prompt4TwoChoice.visible(0)
					desiredALPHA=Lalpha
					desiredX=Rx
					targetALPHA=targetAmean
					targetXXX=targetXmean
					RIGHT=0;
					if phaxxe==5:
						step=step+1
						phaxxe=0
						desiredALPHA=Ralpha
						desiredX=Lx
						targetALPHA=targetAmean
						targetXXX=targetXmean-frodo[stepind]
						RIGHT=1;
						time.sleep(2.5)	# Wait for 5 seconds	
				elif (step==2): #test step, for now assuming the leg leg is the target X
					print("Test, Right=1")					
					messagephase.message('Test')
					desiredALPHA=Ralpha
					desiredX=Lx
					targetALPHA=targetAmean
					targetXXX=targetXmean-frodo[stepind]
					RIGHT=1;
					if (phaxxe==5):#PSYCHO
						reftime = time.time()
						#prompt4TwoChoice = viz.addText('Which Leg had a longer X?',pos=[0,0.4,0],scale=[0.05,0.05,0.05])
						prompt4TwoChoice.visible(1)
						if (PSYCHO!=0) or (time.time()-reftime>=5):
							prompt4TwoChoice.visible(0)
							#time.sleep(10)	# Wait for 5 seconds
							step=step+1
							phaxxe=0
							step=1		
							desiredALPHA=Lalpha
							desiredX=Rx
							targetALPHA=targetAmean
							targetXXX=targetXmean
							RIGHT=0;
							stepind=stepind+1
				else:
					print('Warning phase value un-defined')
			else:
				desiredALPHA=Ralpha
				desiredX=Lx
				targetALPHA=0
				targetXXX=0
						#adjust alpha on right leg
			print ("****************** Trial: ", stepind, " step: ", step, " phase: ", phaxxe, " Alpha of interst: ",  desiredALPHA, " X of interest: ", desiredX,  " TargetX: ", targetXXX, " ******************")
			if (phaxxe == 0):
				#print ("Target Alpha: ", targetALPHA, " Reference Alpha: ", desiredALPHA," Diff: ", targetALPHA-desiredALPHA)
				messagewin.message(str(phaxxe))
				#if (Rz < -30) & (Lz < -30) & ((abs(targetALPHA-desiredALPHA) >= 0.04) or (desiredALPHA >= 0)) & ((abs(targetXXX-desiredX) >= 0.04) or (desiredX >=0 )) : #Undershot the target outside the tolerance of 0.04
				if (Rz < -30) & (Lz < -30) & (abs(targetALPHA-desiredALPHA) >= 0.04)  & (abs(targetXXX-desiredX) >= 0.04) : #Undershot the target outside the tolerance of 0.04
					print ("A. AlphaDiff: ", (targetALPHA-desiredALPHA), " XDiff: ", (targetXXX-desiredX), " RightFirst: ", RIGHT)
					if RIGHT==0:
						Lspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						Rspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
					elif RIGHT==1:
						Rspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						Lspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
				elif (Rz < -30) & (Lz < -30) & (abs(targetALPHA-desiredALPHA) >= 0.04)& (abs(targetXXX-desiredX) < 0.04): # X is coursly satisfied, but the alphas are not
					print ("B. AlphaDiff: ", (targetALPHA-desiredALPHA), " XDiff: ", (targetXXX-desiredX), " RightFirst: ", RIGHT)
					if RIGHT==0:
						Lspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						Rspeed = 0
					elif RIGHT==1:
						Rspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						#Rspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
						Lspeed = 0
				elif (Rz < -30) & (Lz < -30) & (abs(targetALPHA-desiredALPHA) < 0.04)& (abs(targetXXX-desiredX) >= 0.04):# alpha is coursly satisfied, but the Xs are not
					print ("C. AlphaDiff: ", (targetALPHA-desiredALPHA), " XDiff: ", (targetXXX-desiredX), " RightFirst: ", RIGHT)
					if RIGHT==0:
						#Rspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						Rspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
						Lspeed = 0
					elif RIGHT==1:
						Lspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
						Rspeed = 0
				elif (Rz < -30) & (Lz < -30) &(abs(targetALPHA-desiredALPHA) < 0.04) &(abs(targetXXX-desiredX) < 0.04): #Within the target tolerance of 0.04
					Rspeed = 0
					Lspeed = 0
					phaxxe = 2
				else:
					Rspeed = 0
					Lspeed = 0
			#phase 1 move right leg to position
#			elif (phaxxe == 1):
#				#print ("Target X: ", targetXXX, " Reference X: ", desiredX, " Diff: ", targetXXX-desiredX)
#				messagewin.message(str(phaxxe))
#				if (Rz < -30) & (Lz < -30) & (abs(targetXXX-desiredX) >= 0.04):
#					if RIGHT==0:
#						
#						Lspeed = 0
#					elif RIGHT==1:
#						
#						Rspeed = 0
#				elif (Rz < -30) & (Lz < -30) &(abs(targetXXX-desiredX) < 0.04):
#					Lspeed = 0
#					Rspeed = 0
#					phaxxe = 2
#				else:
#					Rspeed = 0
#					Lspeed = 0
					
			#phase 2 move left foot
			elif (phaxxe == 2):
				#print ("Target Alpha: ", targetALPHA, " Reference Alpha: ", desiredALPHA, " Diff: ", targetALPHA-desiredALPHA)
				messagewin.message(str(phaxxe))
				if (Rz < -30) & (Lz < -30) & (abs(targetALPHA-desiredALPHA) >= 0.01):
					if RIGHT==0:
						Lspeed = int(50*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						Rspeed = 0
					elif RIGHT==1:
						Rspeed = int(50*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
						Lspeed = 0
				elif (Rz < -30) & (Lz < -30) &(abs(targetALPHA-desiredALPHA) < 0.01):
					Rspeed = 0
					Lspeed = 0
					phaxxe = 3
				else:
					Rspeed = 0
					Lspeed = 0
			
			#phase 3 pre-pose
			elif (phaxxe == 3):
				messagewin.message(str(phaxxe))
				#print ("Target X: ", targetXXX, " Reference X: ", desiredX, " Diff: ", targetXXX-desiredX)
				if (Rz < -30) & (Lz < -30) & (abs(targetXXX-desiredX) >= 0.01):
					if RIGHT==0:
						Rspeed = int(50*math.copysign(1,(targetXXX-desiredX)))
						Lspeed = 0
					elif RIGHT==1:
						Lspeed = int(50*math.copysign(1,(targetXXX-desiredX)))
						Rspeed = 0
				elif (Rz < -30) & (Lz < -30) &(abs(targetXXX-desiredX) < 0.01):
					Lspeed = 0
					Rspeed = 0
					phaxxe = 5
					
				else:
					Rspeed = 0
					Lspeed = 0
					
			elif (phaxxe == 4):#end of trial move the feet together
				messagewin.message('Test Complete!')
				messagewin.visible(1)
				Rspeed = 0
				Lspeed = 0
			else:
				print('Warning phase value un-defined')
			print(" LeftBeltSpeed: ", Lspeed, " RightBeltSpeed: ", Rspeed)
#			#########################################
#			#adjust alpha on right leg
#			if (phaxxe == 0):
#				#print ("Target Alpha: ", targetALPHA, " Reference Alpha: ", desiredALPHA," Diff: ", targetALPHA-desiredALPHA)
#				messagewin.message(str(phaxxe))
#				if (Rz < -30) & (Lz < -30) & (abs(targetALPHA-desiredALPHA) >= 0.04): #Undershot the target outside the tolerance of 0.04
#					if RIGHT==0:
#						Lspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
#						Rspeed = 0
#						print( " Move the Left Belt AT ", -1*(targetALPHA-desiredALPHA))
#					elif RIGHT==1:
#						Rspeed = int(300*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
#						Lspeed = 0
#						print( " Move the Right Belt AT", -1*(targetALPHA-desiredALPHA))
#				elif (Rz < -30) & (Lz < -30) &(abs(targetALPHA-desiredALPHA) < 0.04): #Within the target tolerance of 0.04
#					Rspeed = 0
#					Lspeed = 0
#					phaxxe = 1
#				else:
#					Rspeed = 0
#					Lspeed = 0
#			#phase 1 move right leg to position
#			elif (phaxxe == 1):
#				#print ("Target X: ", targetXXX, " Reference X: ", desiredX, " Diff: ", targetXXX-desiredX)
#				messagewin.message(str(phaxxe))
#				if (Rz < -30) & (Lz < -30) & (abs(targetXXX-desiredX) >= 0.04):
#					if RIGHT==0:
#						Rspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
#						Lspeed = 0
#					elif RIGHT==1:
#						Lspeed = int(300*math.copysign(1,(targetXXX-desiredX)))
#						Rspeed = 0
#				elif (Rz < -30) & (Lz < -30) &(abs(targetXXX-desiredX) < 0.04):
#					Lspeed = 0
#					Rspeed = 0
#					phaxxe = 2
#				else:
#					Rspeed = 0
#					Lspeed = 0
#					
#			#phase 2 move left foot
#			elif (phaxxe == 2):
#				#print ("Target Alpha: ", targetALPHA, " Reference Alpha: ", desiredALPHA, " Diff: ", targetALPHA-desiredALPHA)
#				messagewin.message(str(phaxxe))
#				if (Rz < -30) & (Lz < -30) & (abs(targetALPHA-desiredALPHA) >= 0.01):
#					if RIGHT==0:
#						Lspeed = int(50*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
#						Rspeed = 0
#					elif RIGHT==1:
#						Rspeed = int(50*math.copysign(1,-1*(targetALPHA-desiredALPHA)))
#						Lspeed = 0
#				elif (Rz < -30) & (Lz < -30) &(abs(targetALPHA-desiredALPHA) < 0.01):
#					Rspeed = 0
#					Lspeed = 0
#					phaxxe = 3
#				else:
#					Rspeed = 0
#					Lspeed = 0
#			
#			#phase 3 pre-pose
#			elif (phaxxe == 3):
#				messagewin.message(str(phaxxe))
#				#print ("Target X: ", targetXXX, " Reference X: ", desiredX, " Diff: ", targetXXX-desiredX)
#				if (Rz < -30) & (Lz < -30) & (abs(targetXXX-desiredX) >= 0.01):
#					if RIGHT==0:
#						Rspeed = int(50*math.copysign(1,(targetXXX-desiredX)))
#						Lspeed = 0
#					elif RIGHT==1:
#						Lspeed = int(50*math.copysign(1,(targetXXX-desiredX)))
#						Rspeed = 0
#				elif (Rz < -30) & (Lz < -30) &(abs(targetXXX-desiredX) < 0.01):
#					Lspeed = 0
#					Rspeed = 0
#					phaxxe = 5
#					
#				else:
#					Rspeed = 0
#					Lspeed = 0
#					
#			elif (phaxxe == 4):#end of trial move the feet together
#				messagewin.message('Test Complete!')
#				messagewin.visible(1)
#				Rspeed = 0
#				Lspeed = 0
#			else:
#				print('Warning phase value un-defined')

				
			#send speed update
			speedlist = [Rspeed,Lspeed,1300,1300,0]#the accelerations "1200 mm/s^2" are not arbitrary! Do not change. Integrate 1200 twice and you'll see that the belts should travel exactly 0.0375 m before stopping. 
			qq.put(speedlist)

			histzR = Rz
			histzL = Lz
			#save data
			savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,RANKY-LANKY,LANKY-RANKY,Ralpha,Lalpha,Rx,Lx,RANKY,LANKY,RGT,LGT,phaxxe, PSYCHO, targetAmean, targetXmean, frodo[stepind], time.time(), stepind, step, phaxxe, desiredALPHA, desiredX, TargetXXX]#organize the data to be written to file			
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
	mststring = str(mst2)+'PSYCHO_X_TwoChoice_V1.txt' # SAVE THE DATA FILES... AS A NAME THAT MAKES SENCE
	print("Data file created named: ")
	print(mststring)
	file = open(mststring,'w+')
	csvw = csv.writer(file)
#	savestring = [FN,Rz,Lz,RHS,LHS,rgorb,lgorb,RANKY-LANKY,LANKY-RANKY,Ralpha,Lalpha,Rx,Lx,RANKY,LANKY,RGT,LGT,phaxxe, PSYCHO, targetAmean, targetXmean, frodo, time]
	csvw.writerow(['FrameNumber','Rfz','Lfz','RHS','LHS','rgorb','lgorb','rgamma','lgamma','Ralpha','Lalpha','Rx','Lx','RANK','LANK','RHIP','LHIP','phase', 'PSYCHO', 'targetAmean', 'targetXmean', 'frodo', 'time', 'stepind', 'step', 'phaxxe', 'desiredALPHA', 'desiredX', 'TargetXXX'])
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
############################################################ 