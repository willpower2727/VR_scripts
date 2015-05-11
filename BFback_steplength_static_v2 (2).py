""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing typical plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 2, upon toe-off the target and cursor disappear. When Heel strike occurs the target is re-displayed and a history marker
shows the subject where they landed. 

Eventually the treadmill will slowly move the displaced foot back to a neutral position...

"""
import viz
import vizshape
import time

viz.go(

viz.FULLSCREEN #run world in full screen
)

#viz.addChild('dojo.osgb')
# code to add the grid to the environment
grid = vizshape.addGrid()

#initExtraWindows()

#viz.MainView.setPosition(0, 0, -1)
#viz.MainView.setEuler(0,0,0)

#set target tolerance for stride length
global targetL
targetL = 0.3

global targetR
targetR = 0.3

global targettol
targettol = 0.05

global boxPELVIS  #stationar box that represents where the centroid of the pelvis markers is located
boxPELVIS = viz.addChild('box.wrl',color=viz.PURPLE)
boxPELVIS.setPosition([0,0,0])
boxPELVIS.setScale([0.05,0.01,0.05])

global boxL   #target for the left foot positioned according to the target and scaled with the tolerance
boxL = viz.addChild('box.wrl',color=viz.BLUE)
boxL.setPosition([-0.09,0,targetL])
boxL.setScale([0.1,0.01, targettol])
boxL.alpha(0.6)

global boxR
boxR = viz.addChild('box.wrl',color=viz.BLUE)
boxR.setPosition([0.09,0,targetR])
boxR.setScale([0.1,0.01,targettol])
boxR.alpha(0.6)

viz.MainView.setPosition(0, 0.75, 0.2)
viz.MainView.setEuler(0,90,0)


# //////////////////////////////////////////////////
# START OF CODE MMSERVER MODULE
# //////////////////////////////////////////////////

# Import the MotionMonitor Server module.
import mmserver

# This is the IP port to use for connecting to clients.  This value must match the one specified in MotionMonitor.  It should not be 50007, since that port is needed by Vizard to connect to the VRPN.
IP_PORT = int('50008')

# Enable physics if you want the server's objects to move smoothly (but this means that other objects will respond to gravity by default).
#viz.phys.enable()

global ballR   #cursor balls
ballR = viz.add('sphere.x', color=viz.RED, scale=[0.02,0.01,0.02], cache=viz.CACHE_NONE)
ballR.setPosition([0.075,0,0])

global ballL
ballL = viz.add('sphere.x', color=viz.GREEN, scale=[0.02,0.01,0.02], cache=viz.CACHE_NONE)
ballL.setPosition([-0.075,0,0])

global HistBallR   #history balls
HistBallR = viz.add('sphere.x', color=viz.YELLOW, scale=[0.02,0.01,0.02], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.075,0,targetR])
HistBallR.alpha(0.9)

global histR
histR = 0

global histL
histL = 0


global HistBallL
HistBallL = viz.add('sphere.x', color=viz.YELLOW, scale=[0.02,0.01,0.02], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.075,0,targetL])
HistBallL.alpha(0.9)

global steplengthL
steplengthL = 0

global steplengthR
steplengthR = 0


# Register callback for our "connected" event.
def onConnected():
	print 'MotionMonitor server connected.'
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
	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream#
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		
		#If all goes as planned, vectorValue[0] is the Y direction, or in other words it's the sagittal plane position. 
		#vectorValue[1] is a constant but is the frontal plane position. Right now this algorithm does not display a frontal plane position based on subject foot position but is arbitrarily fixed
		#vectorValue[2] is the forecplate Zdirection force corresponding to whichever foot the vector comes with (left or right). 
		
		#update Cursor ball position to reflect where the foot is in sagittal plane motion
		ballR.setPosition(- vectorValue[1], 0, vectorValue[0])#move ball according to step time in Z direction
		
		#hide the cursor ball if the foot is behind the pelvis
		if (vectorValue[0] < 0):
			ballR.visible(0)
			HistBallR.visible(0)#turn of the history ball so its not confusing
		else:
			ballR.visible(1)
			HistBallR.visible(1)
			
		#*!*!*!*!*!*!*Hide the target box and cursor when the subject begins to move for the target. Hides upon toe-off. Also hide the history ball
		if (vectorValue[2] == 0):
			boxR.visible(0)
			ballR.visible(0)
			HistBallR.visible(0)
		else:
			boxR.visible(1)
			ballR.visible(1)
			HistBallR.visible(1)
			
			
		#set history ball based on local maximum relative to anterior pelvic Y direction##########################
		#if (vectorValue[0] > histR) & (vectorValue[0] > 0):
		#	HistBallR.setPosition([- vectorValue[1], 0, vectorValue[0]])#update yellow history ball when HS happens
		#	steplengthR = histR
		#	histR = vectorValue[0]
		#else:
		#	histR = vectorValue[0]

		#set history at heel strike####################################
		if (vectorValue[2] < 0) & (histR == 0.0):
			HistBallR.setPosition([- vectorValue[1], 0, vectorValue[0]])#update yellow history ball when HS happens
			steplengthR = vectorValue[0]
			histR = vectorValue[2]
		else:
			histR = vectorValue[2]
			
		if (abs(steplengthR-targetR) <= targettol-0.041):#highlight the target when the target is hit
			boxR.color( viz.WHITE )
		else:
			boxR.color( viz.BLUE )
			
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
		ballL.setPosition(- vectorValue[1], 0, vectorValue[0]) 
		
		#hide cursor ball if foot is posterior to pelvis
		if (vectorValue[0] < 0):
			ballL.visible(0)
			HistBallL.visible(0)
		else:
			ballL.visible(1)
			HistBallL.visible(1)
			
		#*!*!*!*!*!*!*Hide the target box when the subject begins to move for the target. Hides upon toe-off. Also hide history ball
		if (vectorValue[2] == 0):
			boxL.visible(0)
			ballL.visible(0)
			HistBallL.visible(0)
		else:
			boxL.visible(1)
			ballL.visible(1)
			HistBallL.visible(1)
			
			
		#set history ball based on local maximum relative to anterior pelvic Y direction##########################
		#if (vectorValue[0] > histL) & (vectorValue[0] > 0):
		#	HistBallL.setPosition([- vectorValue[1], 0, vectorValue[0]])#update yellow history ball when HS happens
		#	steplengthL = histL
		#	histL = vectorValue[0]
		#else:
		#	histL = vectorValue[0]
		
		if (vectorValue[2] < 0) & (histL == 0.0):
			HistBallL.setPosition([- vectorValue[1], 0, vectorValue[0]])
			steplengthL = vectorValue[0]
			histL = vectorValue[2]
		else:
			histL = vectorValue[2]
		
		if (abs(steplengthL-targetL) <= targettol-0.041):
			boxL.color( viz.WHITE )
		else:
			boxL.color( viz.BLUE )
			
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
