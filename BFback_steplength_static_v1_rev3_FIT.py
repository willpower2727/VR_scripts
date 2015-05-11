""" Biofeedback routine used to train subjects to take a step forward of various length

Subject is intended to stand still on the treadmill wearing typical plugin gait with hip marker set.
Targets are displayed showing how far a subject should step forward.

In version 1 rev2, target remains visible all the time, there is no cursor or feedback.

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
#grid = vizshape.addGrid()

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
'''
global boxPELVIS  #stationar box that represents where the centroid of the pelvis markers is located
boxPELVIS = viz.addChild('box.wrl',color=viz.PURPLE)
boxPELVIS.setPosition([0,0,0])
boxPELVIS.setScale([0.05,0.01,0.05])
'''
global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.0125])
boxL.setPosition([-0.2,targetL-targettol,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.0125])
boxR.setPosition([0.2,targetR-targettol,0])

viz.MainView.setPosition(0, 0.25, -1.25)
viz.MainView.setEuler(0,0,0)


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
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])
cursorR.visible(0)#in this revision, cursor is always off

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])
cursorL.visible(0)

#initialize a neutral position indicator box
global neutralR
global neutralL

neutralR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralR.setPosition([0.2,0,0])

neutralL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.0125,0.0125], cache=viz.CACHE_NONE)
neutralL.setPosition([-0.2,0,0])

global HistBallR
HistBallR = viz.add('box.wrl', color=viz.YELLOW, scale=[0.375,.005,0.0125], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR,0])
HistBallR.alpha(0.8)
HistBallR.visible(0)

global histR
histR = 0

global histL
histL = 0

global HistBallL
HistBallL = viz.add('box.wrl', color=viz.YELLOW, scale=[0.375,.005,0.0125], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL,0])
HistBallL.alpha(0.8)
HistBallL.visible(0)

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
		
		#update Cursor ball position to reflect where the foot is in sagittal plane motion
		cursorR.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		HistBallR.visible(0)#this version feedback is always off
		
		#hide the cursor if the foot is behind the pelvis or if the foot is on the treadmill
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):# | (vectorValue[0] <= psudoR):
			cursorR.visible(0)
			neutralR.visible(1)
			#HistBallR.visible(0)#turn of the history ball so its not confusing
		else:
			cursorR.visible(0)
			neutralR.visible(0)
			#HistBallR.visible(1)
			
		if (vectorValue[0] > targettol) & (vectorValue[2] < 0):
			neutralR.visible(0)
		
		'''
		#*!*!*!*!*!*!*Hide the target box when the subject begins to move for the target. Hides upon toe-off. Also hide the history ball
		if (vectorValue[2] == 0):
			boxR.visible(0)
			HistBallR.visible(0)
		else:
			boxR.visible(1)
			HistBallR.visible(1)
		'''
			
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
		else:
			histR = vectorValue[2]
			
		'''
		if (abs(steplengthR-targetR) <= targettol-0.041):#highlight the target when the target is hit
			boxR.color( viz.WHITE )
		else:
			boxR.color( viz.BLUE )
		'''
		
		#lastly, determine if the right belt needs to move**************************************************
		if (vectorValue[2] < 0) & (vectorValue[0] > 0.02):#subject is on forceplate, and foot is away from neutral
			#print(vectorValue[0])
			#time.sleep(0.5)
			RightBeltSpeed = 0.1
		else:
			RightBeltSpeed = 0
			
		#send speed command as long as there is enough time left in the 30s of capture
		if ((time.time()-mmserver.starttime) > 28):
			#print('session is ending...')
			mmserver.sendScalarValue('RightBeltSpeed',0)
		else:
			mmserver.sendScalarValue('RightBeltSpeed',RightBeltSpeed)
			#print('mmserver starttime was:')
			#print(mmserver.starttime)
			
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
		cursorL.setScale(0.1,vectorValue[0],0.01250)#scale cursor according to step time in Z direction
		
		HistBallL.visible(0)
		
		#hide cursor ball if foot is posterior to pelvis
		if (vectorValue[0] < 0) | (vectorValue[2] < 0):# | (vectorValue[0] <= psudoL):
			cursorL.visible(0)
			neutralL.visible(1)
			#HistBallL.visible(0)
		else:
			cursorL.visible(0)
			neutralL.visible(0)
			#HistBallL.visible(1)
			
		if (vectorValue[0] > targettol) & (vectorValue[2] < 0):
			neutralL.visible(0)
		'''
		#*!*!*!*!*!*!*Hide the target box when the subject begins to move for the target. Hides upon toe-off. Also hide history ball
		if (vectorValue[2] == 0):
			boxL.visible(0)
			HistBallL.visible(0)
		else:
			boxL.visible(1)
			HistBallL.visible(1)
		'''
			
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
		
		'''
		if (abs(steplengthL-targetL) <= targettol-0.041):
			boxL.color( viz.WHITE )
		else:
			boxL.color( viz.BLUE )
		'''
		
		#lastly, determine if the right belt needs to move**************************************************
		if (vectorValue[2] < 0) & (vectorValue[0] > 0.02):#subject is on forceplate, and foot is away from neutral
			#print(vectorValue[0])
			#time.sleep(0.5)
			LeftBeltSpeed = 0.1
		else:
			LeftBeltSpeed = 0
			
		if ((time.time()-mmserver.starttime) > 28):
			#print('time elapsed is:')
			#print(time.time()-starttime1)
			mmserver.sendScalarValue('LeftBeltSpeed',0)
		else:
			mmserver.sendScalarValue('LeftBeltSpeed',LeftBeltSpeed)
		
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
