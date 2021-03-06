﻿""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 3 FINDTARGETS rev1, feedback, cursor, on, targets off

We want the subject to take like 20 steps with each leg  and see where they step and how consistently, then use this information to setup target values and tolerances

RCOUNT and LCOUNT count attempts, not successes. A new variable GOB returns success/failure. This revision also now returns the stride length at each HS

"""
import viz
import vizshape
import time
import vizinfo
import random
import itertools
import math


viz.go(

#viz.FULLSCREEN #run world in full screen
)

#set target tolerance for stride length
global targetL
#targetL = 0.562#units are meters
#targetL = 0.429
targetL = 0.4385
global targetR
#targetR = 0.562
#targetR = 0.429
targetR = 0.4385

global targettol
targettol = 0.025# 5cm

#place quad behind to show movie
#global rvideo
#global lvideo
#global Rquad
#global Lquad

#rvideo = viz.addVideo('RightSuccess0001-0040.avi')
#lvideo = viz.addVideo('LeftSuccess0001-0040.avi')
#rvideo = viz.addVideo('Righthair.avi')
#lvideo = viz.addVideo('Lefthair.avi')
#rvideo.loop()
#lvideo.loop()
#rvideo.play()
#lvideo.play()

#Rquad = viz.addTexQuad(pos=[0.5,targetR,0.10],scale = [.5,.5,0])
#Rquad.texture(rvideo)
#Lquad = viz.addTexQuad(pos=[-0.5,targetL,0.10],scale = [.5,.5,0])
#Lquad.texture(lvideo)

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =20
#setup array of randomly picked steps
global randy
randy  = [1] * STEPNUM + [2] * STEPNUM # create list of 1's and 2's 
random.shuffle(randy)#randomize the order of tests
random.shuffle(randy)#randomize the order of tests again
#print(randy)

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxL.setPosition([-0.2,targetL,0.05])
boxL.visible(0)#hide the targets

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxR.setPosition([0.2,targetR,.05])
boxR.visible(0)#hide the targets in this script

viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[.4,0,0],scale=[0.1,0.1,0.1])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-.46,0,0],scale=[0.1,0.1,0.1])

global Rhits
Rhits = [0] * STEPNUM #pre-allocate a list to keep track of the steps, will be used at the end to calculate the targets and tolerances
global Lhits
Lhits = [0] * STEPNUM
global stepind #this keeps track of the total # of attempts
stepind = 0

global RightBeltSpeed
global LeftBeltSpeed
RightBeltSpeed = 0
LeftBeltSpeed = 0

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.08,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.08,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global histR
histR = 0

global histL
histL = 0

global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)

HistBallL.visible(0)
HistBallR.visible(0)

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

global Rattempts
Rattempts = 0
global Lattempts
Lattempts = 0

# //////////////////////////////////////////////////
# START OF CODE MMSERVER MODULE
# //////////////////////////////////////////////////

# Import the MotionMonitor Server module.
import mmserver

# This is the IP port to use for connecting to clients.  This value must match the one specified in MotionMonitor.  It should not be 50007, since that port is needed by Vizard to connect to the VRPN.
IP_PORT = int('50008')

# Enable physics if you want the server's objects to move smoothly (but this means that other objects will respond to gravity by default).
#viz.phys.enable()

# Register callback for our "connected" event.
def onConnected():
	print 'MotionMonitor server connected.'
	'''
	global starttime1
	starttime1 = time.time()
	print(mmserver.starttime)
'''
viz.callback(mmserver.CONNECTED_EVENT, onConnected)

# Register callback for our "disconnected" event.
def onDisconnected():
	
	global Rhits
	global Lhits
	#calculate the mean step length and stdev and print it
	meanstepR = sum(Rhits)/len(Rhits)
	variance = map(lambda x: (x - meanstepR)**2, Rhits)
	stdevR = math.sqrt(sum(variance)/len(variance))
	
	meanstepL = sum(Lhits)/len(Lhits)
	variance = map(lambda x: (x - meanstepL)**2, Lhits)
	stdevL = math.sqrt(sum(variance)/len(variance))
	
	print 'The average R step length is:'
	print str(meanstepR)
	print 'The R standard deviation is:'
	print str(stdevR)
	
	print 'The average L step length is:'
	print str(meanstepL)
	print 'The L standard deviation is:'
	print str(stdevL)

	print 'MotionMonitor server disconnected.'
	# mmserver.waitForConnection(IP_PORT) # NOTE: if we want the server to be available for another connection after being disconnected, enable this line
viz.callback(mmserver.DISCONNECTED_EVENT, onDisconnected)

# Register callback for our "scalar value received" event.
def onScalarValueReceived(scalarName, scalarValue, invalid):
	return # currently, do nothing
viz.callback(mmserver.SCALAR_VALUE_RECEIVED_EVENT, onScalarValueReceived)

global starttime
# Register callback for our "vector value received" event.
def onVectorValueReceived(vectorName, vectorValue, invalid):
	global ballR
	global ballL
	global HistBallR
	global histR
	global HistBallL
	global histL
	global boxL
	global boxR
	global targettol
	global target
	global steplengthL
	global steplengthR
	global neutralL
	global neutralR
	global randy
	global stepind #this keeps track of the total # of attempts
	global RightBeltSpeed
	global LeftBeltSpeed
	global Rattempts
	global Lattempts
	global Rhits
	global Lhits
	
#*****************************************************************************************************************************************************************************	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
#		mmserver.sendScalarValue('RCOUNT',RCOUNT)# echo attempt #
#		mmserver.sendScalarValue('Rgorb',RGOB)# echo if the latest attempt was good or bad
		mmserver.sendScalarValue('STEPIND',stepind)#echo total # of steps taken
		
		#update Cursor ball position to reflect where the foot is in sagittal plane motion
		cursorR.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		#vectorValue[0] is the difference in Y direction between GT and Ankle markers. e.g. RGY-RANKY
		#vectirValue[1] is meaningless right now
		#vectorValue[2] is Fz for detecting gait events
		
		#hide the cursor ball if the foot is behind the other foot
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):# | (vectorValue[0] <= psudoR):
			cursorR.visible(0)
			neutralR.visible(0)
			#HistBallR.visible(0)#turn of the history ball so its not confusing
		else:
			cursorR.visible(1)
			neutralR.visible(0)
			#HistBallR.visible(1)

		#set history at heel strike, display feedback
		if (vectorValue[2] < -30) & (histR >= -30) & (vectorValue[0] > targetR/4):
#			RCOUNT = RCOUNT+1#keep track of how many HS happen
			stepind = stepind+1
			Rattempts = Rattempts+1
#			rightcounter.message(str(RCOUNT))
			
			if (vectorValue[0] < targettol): #if the step taken was too short, don't give feedback
				HistBallR.visible(0)
				HistBallR.setPosition([0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			else:
#				HistBallR.visible(1)
				HistBallR.setPosition([0.2, vectorValue[0], 0])#update yellow history ball when HS happens
				
			steplengthR = vectorValue[0] #get the current distance between 
			histR = vectorValue[2]
			rightcounter.message(str(Rattempts))#display how many steps have been taken
			Rhits[Rattempts] = steplengthR#keep record in the list
			neutralL.visible(0)
			neutralR.visible(0)

#			if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit
#				boxR.color( viz.WHITE )
#				RCOUNT = RCOUNT+1#keep track of how many HS happen
#				rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
#				rightcounter.message(str(Rattempts))#only displat attempts since there is no target
#				rightcounter.message(str(2*RCOUNT/stepind)+'/'+str(20))
#				rvideo.play()
#				RGOB = 1
#			else:
#				boxR.color( viz.BLUE )
#				RGOB = 0
#				rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
#				rightcounter.message(str(Rattempts))
				
		else:
			histR = vectorValue[2]
			
		#see if it is time to hide everything before the next step
		if (vectorValue[0] < targetR/2) & (vectorValue[0] > targetR/2-0.01) & (vectorValue[2] < -30):#this changes the targets when the moving leg is half-way back
#				boxR.color( viz.BLUE )#change colors of targets back to default blue
#				boxL.color( viz.BLUE )
#				boxR.visible(0)
#				boxL.visible(0)
#				HistBallR.visible(0)#hide until the next HS
#				HistBallL.visible(0)
				neutralR.visible(0)
				neutralL.visible(0)

						
		#lastly, determine if the right belt needs to move
		if (vectorValue[2] < -10) & (vectorValue[0] > 0.05):#subject is on forceplate, and foot is away from neutral
			#print(vectorValue[0])
			#time.sleep(0.1)
			RightBeltSpeed = 0.2
			mmserver.sendScalarValue('RightBeltSpeed',RightBeltSpeed)
		else:
			RightBeltSpeed = 0
			mmserver.sendScalarValue('RightBeltSpeed',RightBeltSpeed)
			
		if (RightBeltSpeed == 0) & (LeftBeltSpeed == 0):
			if (randy[stepind]  == 1):#when the feet are back together, display the new target
				neutralR.visible(1)
				neutralL.visible(0)
			else:
				neutralR.visible(0)
				neutralL.visible(1)
		'''	
		#send speed command as long as there is enough time left in the 30s of capture
		if ((time.time()-mmserver.starttime) > 158):
			print('session is ending...')
			mmserver.sendScalarValue('RightBeltSpeed',0)
		else:
			mmserver.sendScalarValue('RightBeltSpeed',RightBeltSpeed)
			'''
			#print('mmserver starttime was:')
			#print(mmserver.starttime)
#*****************************************************************************************************************************************************************************			
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
#		mmserver.sendScalarValue('LCOUNT',LCOUNT)
#		mmserver.sendScalarValue('Lgorb',LGOB)
		mmserver.sendScalarValue('STEPIND',stepind)
		
		cursorL.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		#hide cursor ball if foot is posterior to pelvis
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):# | (vectorValue[0] <= psudoL):
			cursorL.visible(0)
			neutralL.visible(0)
			#HistBallL.visible(0)
		else:
			cursorL.visible(1)
			neutralL.visible(0)
			#HistBallL.visible(1)
			
		#detect left HS
		if (vectorValue[2] < -30) & (histL >= -30) & (vectorValue[0] > targetL/4):
#			LCOUNT = LCOUNT+1
			stepind = stepind+1
			Lattempts = Lattempts+1
			leftcounter.message(str(Lattempts))
			steplengthL = vectorValue[0]
			histL = vectorValue[2]
			Lhits[Lattempts] = steplengthL
			neutralL.visible(0)
			neutralR.visible(0)
			
			if (vectorValue[0] < targettol):
				HistBallL.visible(0)
				HistBallL.setPosition([-0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			else:
#				HistBallL.visible(1)
				HistBallL.setPosition([-0.2, vectorValue[0], 0])#update yellow history ball when HS happens

			#check which target should be visible next
#			randy = random.randint(1,2)#this generates a new value for randy to say which leg to test next
#			if (abs(steplengthL-targetL) <= targettol):
#				boxL.color( viz.WHITE )
#				LCOUNT = LCOUNT+1
#				leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
#				leftcounter.message(str(Lattempts))
#				lvideo.play()
#				LGOB = 1
#			else:
#				boxL.color( viz.BLUE )
#				LGOB = 0
#				leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
#				leftcounter.message(str(Lattempts))
				
		else:
			histL = vectorValue[2]
		
		#see if it is time to display the new target
		if (vectorValue[0] < targetL/2) & (vectorValue[0] > targetL/2-0.01) & (vectorValue[2] < -30):#this changes teh targets when the moving leg is half-way back
#				boxR.color( viz.BLUE )
#				boxL.color( viz.BLUE )
#				boxR.visible(0)
#				boxL.visible(0)
#				HistBallR.visible(0)
#				HistBallL.visible(0)
				neutralR.visible(0)
				neutralL.visible(0)
		
		#lastly, determine if the right belt needs to move**************************************************
		if (vectorValue[2] < 0) & (vectorValue[0] > 0.05):#subject is on forceplate, and foot is away from neutral
			#print(vectorValue[0])
			#time.sleep(0.5)
			LeftBeltSpeed = 0.2
			mmserver.sendScalarValue('LeftBeltSpeed',LeftBeltSpeed)
		else:
			LeftBeltSpeed = 0
			mmserver.sendScalarValue('LeftBeltSpeed',LeftBeltSpeed)
			
		if (RightBeltSpeed == 0) & (LeftBeltSpeed == 0):
			if (randy[stepind] == 1):
				neutralR.visible(1)
				neutralL.visible(0)
			else:
				neutralR.visible(0)
				neutralL.visible(1)
			'''
		if ((time.time()-mmserver.starttime) > 158):
			#print('time elapsed is:')
			#print(time.time()-starttime1)
			mmserver.sendScalarValue('LeftBeltSpeed',0)
		else:
			mmserver.sendScalarValue('LeftBeltSpeed',LeftBeltSpeed)
			'''
viz.callback(mmserver.VECTOR_VALUE_RECEIVED_EVENT, onVectorValueReceived)

# Register callback for our "quat value received" event.
def onQuatValueReceived(quatName, quatValue, invalid):
	return # currently, do nothing
viz.callback(mmserver.QUAT_VALUE_RECEIVED_EVENT, onQuatValueReceived)

# Now that everything is set up, tell the server to wait for a connection from MotionMonitor.  This call is non-blocking and will return immediately.
mmserver.waitForConnection(IP_PORT)

# ////////////////////////////////////////////////
# END OF CODE MMSERVER MODULE
# ////////////////////////////////////////////////
