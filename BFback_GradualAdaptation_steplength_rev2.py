#script runs biofeedback routine with TMM, Vicon. Gives feedback on the length of step 
#while in gait. 

#revision 2 uses footprints, waits for 3 steps before displaying new target value

import viz
import vizshape
import time
import vizinfo

viz.go(

viz.FULLSCREEN #run world in full screen
)

#set target tolerance for stride length
global targetL
targetL = 0.3

global targetR
targetR = 0.3

global targettol
targettol = 0.025

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.005])
boxL.setPosition([-0.2,targetL,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.005])
boxR.setPosition([0.2,targetR,0])

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

#variables used to keep track of gait events
global Rforceold
global Lforceold
Rforceold = 0
Lforceold = 0

# //////////////////////////////////////////////////
# START OF CODE DEMONSTRATING USE OF MMSERVER MODULE
# //////////////////////////////////////////////////

# Import the MotionMonitor Server module.
import mmserver

# This is the IP port to use for connecting to clients.  This value must match the one specified in MotionMonitor.  It should not be 50007, since that port is needed by Vizard to connect to the VRPN.
IP_PORT = int('50008')

# Enable physics if you want the server's objects to move smoothly (but this means that other objects will respond to gravity by default).
#viz.phys.enable()

global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])

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

# Register callback for our "connected" event.
def onConnected():
	print 'MotionMonitor server connected.'
viz.callback(mmserver.CONNECTED_EVENT, onConnected)

# Register callback for our "disconnected" event.
def onDisconnected():
	print 'MotionMonitor server disconnected.'
	# mmserver.waitForConnection(IP_PORT) # NOTE: if we want the server to be available for another connection after being disconnected, enable this line
viz.callback(mmserver.DISCONNECTED_EVENT, onDisconnected)

# Register callback for our "calibration file generated" event.
#def onCalibrationFileGenerated(calibrationFileName):
#	print 'Calibration file generated.'
#	import pickle
#	with open(calibrationFileName, 'rb') as file:
#		data = pickle.load(file)      # load the data from the calibration file
#	animator.setCalibrationData(data) # send the calibration data to the animator module... this should make the avatar's segments snap into their correct positions
#viz.callback(mmserver.CALIBRATION_FILE_GENERATED_EVENT, onCalibrationFileGenerated)

# Register callback for our "scalar value received" event.
def onScalarValueReceived(scalarName, scalarValue, invalid):
	return # currently, do nothing
viz.callback(mmserver.SCALAR_VALUE_RECEIVED_EVENT, onScalarValueReceived)

# Register callback for our "vector value received" event.
def onVectorValueReceived(vectorName, vectorValue, invalid):
	global cursorR
	global cursorL
	global HistBallR
	global histR
	global HistBallL
	global histL
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
	global Rforceold
	global Lforceold
	global Rtop
	global Rhsp
	global Ltop
	global Lhsp
	
	
	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream#
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		mmserver.sendScalarValue('RCOUNT',RCOUNT)
		#vectorValue[0] is the step length, vectorValue[2] is the forceplate data
		
		#update the cursor position every time vector is recieved
		cursorR.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		#Determine whether or not the cursor should be visible. If the foot of interest is behind the pelvis, it should disappear
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):
			cursorR.visible(0)
			#histballR.visible(0)
		else:
			cursorR.visible(1)
			#histballR.visible(1)

		#set history at heel strike####################################
		if (vectorValue[2] < 0) & (histR == 0.0):
			HistBallR.setPosition([0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			steplengthR = vectorValue[0]
			histR = vectorValue[2]
		else:
			histR = vectorValue[2]
			
		if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit
			boxR.color( viz.WHITE )
		else:
			boxR.color( viz.BLUE )
			
		#if successful step was taken, keep track of it
		if (vectorValue[2] < -20) & (Rforceold == 0.0) & (abs(steplengthR-targetR) <= targettol):
			RCOUNT = RCOUNT+1
			#rightcounter.setText(str(RCOUNT))
			rightcounter.message(str(RCOUNT))
		
		#see if it is time to calculate the step length
		if (vectorValue[2] == 0) & (Rforceold < 0):#toe off condition
			#calculate Toe-Off position
			Rtop = vectorValue[0]
		elif (vectorValue[2] < -20) & (Rforceold == 0):#HS condition
			Rhsp = vectorValue[0]
			psudoR = psudoR +1
			if (psudoR == 5):
				boxR.setPosition([0.2,0.5*(Rhsp-Rtop),0])
				targetR = 0.5*(Rhsp-Rtop)
				psudoR = 1
		
		Rforceold = vectorValue[2]#save current force value for next time vector is recieved
			
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
		mmserver.sendScalarValue('LCOUNT',LCOUNT)
	
		cursorL.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):
			cursorL.visible(0)
		else:
			cursorL.visible(1)
		#set history ball based on local maximum relative to anterior pelvic Y direction##########################
		#if (vectorValue[0] > histL) & (vectorValue[0] > 0):
		#	HistBallL.setPosition([- vectorValue[1], 0, vectorValue[0]])#update yellow history ball when HS happens
		#	steplengthL = histL
		#	histL = vectorValue[0]
		#else:
		#	histL = vectorValue[0]
		
		if (vectorValue[2] < 0) & (histL == 0.0):
			HistBallL.setPosition([-0.2,vectorValue[0],0])
			steplengthL = vectorValue[0]
			histL = vectorValue[2]
		else:
			histL = vectorValue[2]
		
		if (abs(steplengthL-targetL) <= targettol):
			boxL.color( viz.WHITE )
		else:
			boxL.color( viz.BLUE )
			
		if (vectorValue[2] < -20) & (Lforceold == 0.0) & (abs(steplengthL-targetL) <= targettol):
			LCOUNT = LCOUNT+1
			leftcounter.message(str(LCOUNT))
			
		#see if it is time to calculate the step length
		if (vectorValue[2] == 0) & (Lforceold < 0):#toe off condition
			#calculate Toe-Off position
			Ltop = vectorValue[0]
		elif (vectorValue[2] < -20) & (Lforceold == 0):#HS condition
			Lhsp = vectorValue[0]
			psudoL = psudoL +1
			if (psudoL == 5):
				boxL.setPosition([-0.2,0.5*(Lhsp-Ltop),0])
				targetL = 0.5*(Lhsp-Ltop)
				psudoL = 1
		
		Lforceold = vectorValue[2]
		
			
viz.callback(mmserver.VECTOR_VALUE_RECEIVED_EVENT, onVectorValueReceived)


# Register callback for our "quat value received" event.
def onQuatValueReceived(quatName, quatValue, invalid):
	return # currently, do nothing
viz.callback(mmserver.QUAT_VALUE_RECEIVED_EVENT, onQuatValueReceived)

# Now that everything is set up, tell the server to wait for a connection from MotionMonitor.  This call is non-blocking and will return immediately.
mmserver.waitForConnection(IP_PORT)

# ////////////////////////////////////////////////
# END OF CODE DEMONSTRATING USE OF MMSERVER MODULE
# ////////////////////////////////////////////////
