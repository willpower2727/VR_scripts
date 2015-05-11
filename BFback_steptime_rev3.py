""" Biofeedback routine for step time, from HS to HS

This script updates left and right cursors based on step time, using a flip-flop technique

WDA 5/12/2014
includes footprint instead of history bar
"""


import viz
import vizshape

viz.go(

viz.FULLSCREEN
)

#set target tolerance for step time
global targetL
targetL = 0.5

global targetR
targetR = 0.5

global targettol
targettol = 0.05

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxL.setPosition([-0.2,targetL,0.05])#target box needs to be a little offset from pure target altittude since perspective can make biofeedback seem dishonest, good feedback appears when it looks like value is outside target box

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxR.setPosition([0.2,targetR,0.05])

viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)



# //////////////////////////////////////////////////
# START OF CODE DEMONSTRATING USE OF MMSERVER MODULE
# //////////////////////////////////////////////////

# Import the MotionMonitor Server module.
import mmserver

# This is the IP port to use for connecting to clients.  This value must match the one specified in MotionMonitor.  It should not be 50007, since that port is needed by Vizard to connect to the VRPN.
IP_PORT = int('50008')

# Enable physics if you want the server's objects to move smoothly (but this means that other objects will respond to gravity by default).
#viz.phys.enable()

# Add a purple ball to our world, whose position will later be updated by the data we receive.
global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.025])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.025])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
#HistBallR.setEuler(180,0,0)
HistBallR.alpha(0.8)

global histR
histR = 0

global histL
histL = 0


global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.02,0.02,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallR.setEuler(180,0,0)
HistBallL.alpha(0.8)

global flipflop
flipflop = 0

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
	global target
	global steptimeL
	global steptimeR
	global flipflop
	
	steptimeR = 0
	steptimeL = 0
	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream#
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		
		#IMPORTANT: vectorValue[0] is RHS, vectorValue[1] is LHS, vectorValue[2] is HS
		
		if vectorValue[0] == 1:#L to R
			cursorR.setScale(0.1,vectorValue[2],0.0125)#move cursor according to step time in Z direction
			cursorL.setScale(0.1,0.01,0.0125);#minimize the other cursor
			histR = vectorValue[2]
			#boxR.color( viz.BLUE )
			
			if (vectorValue[2] <= 0.1):
				HistBallL.setPosition([-0.2, histL, 0])#update yellow history bar when HS happens
				steptimeL = histL
			
			if (abs(histL-targetL) <= targettol):#highlight the target when the target is hit
				boxL.color( viz.WHITE )
			else:
				boxL.color( viz.BLUE )
			
		elif vectorValue[0] == 0:#R to L
			cursorL.setScale(0.1,vectorValue[2],0.0125)#move cursor according to step time in Z direction
			cursorR.setScale(0.1,0.01,0.0125);
			histL = vectorValue[2]
			#boxL.color( viz.BLUE )
			
			if (vectorValue[2] <= 0.1):
				HistBallR.setPosition([0.2, histR, 0])#update yellow history bar when HS happens
				steptimeR = histR
			
			if (abs(histR-targetR) <= targettol):#highlight the target when the target is hit
				boxR.color( viz.WHITE )
			else:
				boxR.color( viz.BLUE )
			
		#**!!! Not going to use two vectors being passed in since step time will be one variable.
			'''
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
		cursorL.setScale(0.1,vectorValue[2],0.0125) 
		if (vectorValue[2] <= 0.1):
			HistBallL.setPosition([-0.2, histL, 0])
			steptimeL = histL
		else:
			histL = vectorValue[2]
		
		if (abs(steptimeL-targetL) <= targettol):
			boxL.color( viz.WHITE )
		else:
			boxL.color( viz.BLUE )
			'''
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
