""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 3 rev6, feedback, cursor, and target are on.

Treadmill moves the feet back to neutral after a step

rev 6 uses a pseudo-randomized test of each leg. A vector of steps is randomly assigned to match how many steps need to be taken.

RCOUNT and LCOUNT count attempts, not successes. A new variable GOB returns success/failure. This revision also now returns the stride length at each HS

"""
import viz
import vizshape
import time
import vizinfo
import random
import itertools

viz.go(

viz.FULLSCREEN #run world in full screen
)

#set target tolerance for stride length
global targetL
targetL = 0.562#units are meters

global targetR
targetR = 0.562

global targettol
targettol = 0.05# 5cm

#declare the total number of steps to attempt (this is the accumulation of steps total, i.e. 75 R and 75 L means 150 total attempts)
global STEPNUM
STEPNUM = 40
#setup array of randomly picked steps
global randy
randy  = [1] * STEPNUM + [2] * STEPNUM # create list of 1's and 2's 
random.shuffle(randy)#randomize the order of tests
#print(randy)

global boxL #left target box
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxL.setPosition([-0.2,targetL,0.05])

global boxR #right target box
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol+.019,0.0125])
boxR.setPosition([0.2,targetR,.05])

viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)


#FIRE!
fire = viz.add('fire.osg',scale=[1,1,1])
fire.setPosition(-0.2,targetL,0.05)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR+0.6,12])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-4.6,targetL+0.6,12])

#global RightBeltSpeed
#RightBeltSpeed = 0
#global LeftBeltSpeed
#LeftBeltSpeed = 0
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


# //////////////////////////////////////////////////
# START OF CODE MMSERVER MODULE
# //////////////////////////////////////////////////

# Import the MotionMonitor Server module.
import mmserver

# This is the IP port to use for connecting to clients.  This value must match the one specified in MotionMonitor.  It should not be 50007, since that port is needed by Vizard to connect to the VRPN.
IP_PORT = int('50008')

# Enable physics if you want the server's objects to move smoothly (but this means that other objects will respond to gravity by default).
#viz.phys.enable()

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.4,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
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

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0

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
#	global RightBeltSpeed
#	global LeftBeltSpeed
	global RGOB
	global LGOB
	global stepind #this keeps track of the total # of attempts
	global RightBeltSpeed
	global LeftBeltSpeed
	
#*****************************************************************************************************************************************************************************	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		mmserver.sendScalarValue('RCOUNT',RCOUNT)# echo attempt #
		mmserver.sendScalarValue('Rgorb',RGOB)# echo if the latest attempt was good or bad
		mmserver.sendScalarValue('STEPIND',stepind)#echo total # of steps taken
		
		#update Cursor ball position to reflect where the foot is in sagittal plane motion
		cursorR.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
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
		if (vectorValue[2] < -30) & (histR >= -30):
			RCOUNT = RCOUNT+1#keep track of how many HS happen
			stepind = stepind+1
			rightcounter.message(str(RCOUNT))
			
			if (vectorValue[0] < targettol): #if the step taken was too short, don't give feedback
				HistBallR.visible(0)
				HistBallR.setPosition([0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			else:
				HistBallR.visible(1)
				HistBallR.setPosition([0.2, vectorValue[0], 0])#update yellow history ball when HS happens
				
			steplengthR = vectorValue[0] #get the current distance between 
			histR = vectorValue[2]
			#check which target should be visible next
#			randy = random.randint(1,2)#this generates a new value for randy to say which leg to test next
			
			if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit
				boxR.color( viz.WHITE )
				RGOB = 1
			else:
				boxR.color( viz.BLUE )
				RGOB = 0
				
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
		
		cursorL.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
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
		if (vectorValue[2] < -30) & (histL >= -30):
			LCOUNT = LCOUNT+1
			stepind = stepind+1
			leftcounter.message(str(LCOUNT))
			
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
				boxL.color( viz.WHITE )
				LGOB = 1
			else:
				boxL.color( viz.BLUE )
				LGOB = 0
			
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
