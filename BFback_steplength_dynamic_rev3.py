#script runs biofeedback routine with TMM, Vicon. Gives feedback on the length of step 
#while in gait. 

#revision 4 incorps. footprint as history marker instead of a bar

import viz
import vizshape
import time

viz.go(

viz.FULLSCREEN #run world in full screen
)

#viz.addChild('dojo.osgb')
# code to add the grid to the environment
#grid = vizshape.addGrid()


#viz.MainView.setPosition(0, 0, -1)
#viz.MainView.setEuler(0,0,0)

#set target tolerance for stride length
global targetL
targetL = 0.3

global targetR
targetR = 0.3

global targettol
targettol = 0.05
'''
global boxPELVIS
boxPELVIS = viz.addChild('box.wrl',color=viz.PURPLE)
boxPELVIS.setPosition([0,0,0])
boxPELVIS.setScale([0.05,0.025,0.05])
'''
global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxL.setPosition([-0.2,targetL,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxR.setPosition([0.2,targetR,0])

viz.MainView.setPosition(0, 0.25, -1.25)
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
	global steplengthL
	global steplengthR
	global psudoR
	global psudoL
	
	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream#
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		
		#vectorValue[0] is the step length, vectorValue[2] is the forceplate data
		
		cursorR.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):
			cursorR.visible(0)
			#histballR.visible(0)
		else:
			cursorR.visible(1)
			#histballR.visible(1)
			
		#set history ball based on local maximum relative to anterior pelvic Y direction##########################
		#if (vectorValue[0] > histR) & (vectorValue[0] > 0):
		#	HistBallR.setPosition([- vectorValue[1], 0, vectorValue[0]])#update yellow history ball when HS happens
		#	steplengthR = histR
		#	histR = vectorValue[0]
		#else:
		#	histR = vectorValue[0]

		#set history at heel strike####################################
		if (vectorValue[2] < 0) & (histR == 0.0):
			HistBallR.setPosition([0.2, vectorValue[0], 0])#update yellow history ball when HS happens
			steplengthR = vectorValue[0]
			histR = vectorValue[2]
			
			#if (vectorValue[0] < 0.1):#do not show history when HS is a return to neutral stance
			#	histballR.visible(0)
			#else:
			#	histballR.visible(1)
		else:
			histR = vectorValue[2]
			
		if (abs(steplengthR-targetR) <= targettol):#highlight the target when the target is hit
			boxR.color( viz.WHITE )
		else:
			boxR.color( viz.BLUE )
			
		#set a variable up to do a psudo differentiation check
		psudoR = vectorValue[0]
			
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
		
	
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
			
		psudoL = vectorValue[0]
			
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
