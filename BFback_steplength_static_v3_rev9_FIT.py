﻿""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 3 rev9, feedback, cursor, and target are on.

Treadmill moves the feet back to neutral after a step

rev9 introduces a new method of scaling the world objects so that different targets can be displayed for the left and right targets but they appear to be the same size by
changing the perspective and lighting

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

viz.MainView.setPosition(0,0,-1)
viz.MainView.setEuler(0,0,0)


#set target tolerance for stride length
global targetL
targetL = 0.565
global targetR
targetR = 0.566

global targettolR
global targettolL
targettolL = 0.131*0.5# 5cm
targettolR = 0.132*0.5

#compute the perspective variables
#assume the left target stays put

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettolL,0.0125])
boxL.setPosition([-0.175,0,1])

cscale = boxL.getScale(	 mode = viz.ABS_PARENT	) 
print 'cscale is:'
print str(cscale)
global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[1.2*cscale[0],0.25,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.175,-targetL,1])
global neutralL
neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[1.2*cscale[0],0.5*cscale[1],0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.165,-0.25,0.95])
global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.8*targettolL,0.8*targettolL,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.175,0,1])
HistBallL.alpha(0.8)

global lscaler

lscaler = 1

###############

global Rdistance

theta1 = 2*math.atan2(targettolL,2*1)#for the height
#print 'Theta1 is:'
#print str(theta1)
Rdistance = targettolR/math.tan(theta1)
#print 'distance R back is:'
#print str(Rdistance)
theta2 = 2*math.atan2(0.1,2*1)#for the width of the right target
rscale1 = Rdistance*math.tan(theta2)
#print 'width scale is:'
#print str(rscale1)
theta3 = 2*math.atan2(0.175,2*1)#for the Left to Right position of the Right target
rxdistance = Rdistance*math.tan(theta3)
#print 'Rx distance is:'
#print str(rxdistance)
theta4 = 2*math.atan2(targetL,2*1)#for the initial height of the cursor
rcursescale = Rdistance*math.tan(theta4)

global rscaler
rscaler = 0.25/targetR

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[rscale1,targettolR,0.0125])
boxR.setPosition([rxdistance,0,Rdistance])
global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[1.2*rscale1,rcursescale,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([rxdistance,-rcursescale,Rdistance])
global neutralR
neutralR = viz.add('box3.obj', color=viz.RED, scale=[1.2*cscale[0],0.5*cscale[1],0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.165,-0.25,0.95])
global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.8*targettolR,0.8*targettolR,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([rxdistance,0,Rdistance])
HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

#Add an extra light so the left target looks almost as bright as the right one
newlight = viz.addLight();
newlight.setPosition([-1,0,0.25])
newlight.intensity(1.5)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[.4,-0.25,1],scale=[0.1,0.1,0.1])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-.46,-0.25,1],scale=[0.1,0.1,0.1])

global RGOB
RGOB = 0 #this will be 0 or 1, depending on success or failure
global LGOB
LGOB = 0
global stepind #this keeps track of the total # of attempts
stepind = 0

global RightBeltSpeed
global LeftBeltSpeed
RightBeltSpeed = 0
LeftBeltSpeed = 0

global histR
histR = 0

global histL
histL = 0

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

global Rattempts
Rattempts = 0
global Lattempts
Lattempts = 0

#load exploding target osg's
global rxplode
global lxplode

rxplode = 0
lxplode = 0

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM =20
#setup array of randomly picked steps
global randy
randy  = [1] * STEPNUM + [2] * STEPNUM # create list of 1's and 2's 
random.shuffle(randy)#randomize the order of tests
random.shuffle(randy)#randomize the order of tests again
#print(randy)

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
	global RCOUNT
	global LCOUNT
	global randy
	global RGOB
	global LGOB
	global stepind #this keeps track of the total # of attempts
	global RightBeltSpeed
	global LeftBeltSpeed
	global rxplode
	global lxplode
	global Rattempts
	global Lattempts
	global Rdistance
	global lscaler
#	global rscaler
#*****************************************************************************************************************************************************************************	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		mmserver.sendScalarValue('RCOUNT',RCOUNT)# echo attempt #
		mmserver.sendScalarValue('Rgorb',RGOB)# echo if the latest attempt was good or bad
		mmserver.sendScalarValue('STEPIND',stepind)#echo total # of steps taken
		
		#update Cursor ball position to reflect where the foot is in sagittal plane motion
		cursorR.setScale(1.2*rscale1,Rdistance*math.tan(2*math.atan2(vectorValue[0],2*1)),0.0125)#scale cursor according to step time in Z direction
		
		#vectorValue[0] is the difference in Y direction between GT and Ankle markers. e.g. RGY-RANKY
		#vectirValue[1] is meaningless right now
		#vectorValue[2] is Fz for detecting gait events
		
		#hide the cursor ball if the foot is behind the other foot
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):# | (vectorValue[0] <= psudoR):
			cursorR.visible(0)
			neutralR.visible(1)
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
				HistBallR.setPosition([rxdistance,Rdistance*math.tan(2*math.atan2(vectorValue[0],2*1)),Rdistance])#update yellow history ball when HS happens
			else:
				HistBallR.visible(1)
				HistBallR.setPosition([rxdistance,Rdistance*math.tan(2*math.atan2(vectorValue[0],2*1)),Rdistance])#update yellow history ball when HS happens
				
			steplengthR = vectorValue[0] #get the current distance between 
			histR = vectorValue[2]
			#check which target should be visible next
			
			if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit
#				boxR.visible(0)
				RCOUNT = RCOUNT+1#keep track of how many HS happen
				rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
				rxplode = viz.addChild('targetexplode13.osgb',pos=[0.2,targetR,0.05],scale=[0.1,targettol+.019,0.0125])#make the target explode
				rxplode.setAnimationState(0)
				boxR.visible(0)
				RGOB = 1
			else:
				boxR.color( viz.BLUE )
				RGOB = 0
				rightcounter.message(str(RCOUNT)+'/'+str(Rattempts))
				
		else:
			histR = vectorValue[2]
			
		#see if it is time to hide everything before the next step
		if (vectorValue[0] < targetR/2) & (vectorValue[0] > targetR/2-0.01) & (vectorValue[2] < -30):#this changes the targets when the moving leg is half-way back
				boxR.color( viz.BLUE )#change colors of targets back to default blue
				boxL.color( viz.BLUE )
				boxR.visible(0)
				boxL.visible(0)
				HistBallR.visible(0)#hide until the next HS
				HistBallL.visible(0)
				rxplode.remove()

						
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
				boxR.visible(1)
				boxL.visible(0)
			else:
				boxR.visible(0)
				boxL.visible(1)
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
		mmserver.sendScalarValue('LCOUNT',LCOUNT)
		mmserver.sendScalarValue('Lgorb',LGOB)
		mmserver.sendScalarValue('STEPIND',stepind)
		
		cursorL.setScale(0.1,vectorValue[0]*lscaler,0.01250)#scale cursor according to step time in Z direction
		
		#hide cursor ball if foot is posterior to pelvis
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):# | (vectorValue[0] <= psudoL):
			cursorL.visible(0)
			neutralL.visible(1)
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
#			leftcounter.message(str(LCOUNT))
			
			if (vectorValue[0] < targettol):
				HistBallL.visible(0)
				HistBallL.setPosition([-0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			else:
				HistBallL.visible(1)
				HistBallL.setPosition([-0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			steplengthL = vectorValue[0]
			histL = vectorValue[2]
			#check which target should be visible next
#			randy = random.randint(1,2)#this generates a new value for randy to say which leg to test next
			if (abs(steplengthL-targetL) <= targettol):
#				boxL.visible(0)
				LCOUNT = LCOUNT+1
				leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
				lxplode = viz.addChild('targetexplode13.osgb',pos=[-0.2,targetL,0],scale=[0.1,(targettol+0.19),0.0125])
				lxplode.setAnimationState(0)
				boxL.visible(0)
				LGOB = 1
			else:
				boxL.color( viz.BLUE )
				LGOB = 0
				leftcounter.message(str(LCOUNT)+'/'+str(Lattempts))
			
		else:
			histL = vectorValue[2]
		
		#see if it is time to display the new target
		if (vectorValue[0] < targetL/2) & (vectorValue[0] > targetL/2-0.01) & (vectorValue[2] < -30):#this changes teh targets when the moving leg is half-way back
				boxR.color( viz.BLUE )
				boxL.color( viz.BLUE )
				boxR.visible(0)
				boxL.visible(0)
				HistBallR.visible(0)
				HistBallL.visible(0)
				lxplode.remove()
		
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
				boxR.visible(1)
				boxL.visible(0)
			else:
				boxR.visible(0)
				boxL.visible(1)
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
