#Stridetime revision 5 incorporates the footprint as history bar, and introduces a counter to display the # of successful stride times.
#WDA 6/4/2014

import viz
import vizshape
import vizinfo

viz.go(

viz.FULLSCREEN
)

#viz.MainView.setPosition(0, 0, -1)
#viz.MainView.setEuler(0,0,0)

#setup a variable to scale the height of objects so that the screen setup is optimized for viewing base on target values
global scalorxx
scalorxx = 0.6667

#set target tolerance for step time
global targetL
targetL = 1

global targetR
targetR = 1

global targettol
targettol = 0.05

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.04)*0.75,0.0125])
boxL.setPosition([-0.2,targetL*scalorxx,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.04)*0.75,0.0125])
boxR.setPosition([0.2,targetR*scalorxx,0])

viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)

#setup counter panels
global RCOUNT
global LCOUNT
RCOUNT = 0
LCOUNT = 0
#rightcounter = vizinfo.InfoPanel(str(RCOUNT),align=viz.ALIGN_RIGHT_TOP,fontSize=50,icon=False,key=None)
rightcounter = viz.addText(str(RCOUNT),pos=[4,targetR+0.6,12])
#leftcounter = vizinfo.InfoPanel(str(LCOUNT),align=viz.ALIGN_LEFT_TOP,fontSize=50,icon=False,key=None)
leftcounter = viz.addText(str(LCOUNT),pos=[-4.4,targetL+0.6,12])

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

# Add a purple ball to our world, whose position will later be updated by the data we receive.
global cursorR
cursorR = viz.add('box3.obj', color=viz.RED, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorR.setPosition([0.2,0,0.05])

global cursorL
cursorL = viz.add('box3.obj', color=viz.GREEN, scale=[0.1,0.1,0.0125], cache=viz.CACHE_NONE)
cursorL.setPosition([-0.2,0,0.05])

global HistBallR
HistBallR = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.03,0.03,0.1], cache=viz.CACHE_NONE)
HistBallR.setPosition([0.2,targetR*scalorxx,0])
HistBallR.setEuler(0,0,0)
HistBallR.alpha(0.8)

global histR
histR = 0

global histL
histL = 0


global HistBallL
HistBallL = viz.add('footprint2.obj', color=viz.YELLOW, scale=[0.03,0.03,0.1], cache=viz.CACHE_NONE)
HistBallL.setPosition([-0.2,targetL*scalorxx,0])
HistBallR.setEuler(180,0,0)
HistBallL.alpha(0.8)

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
	global scalorxx
	global RCOUNT
	global LCOUNT
	global Rforceold
	global Lforceold
	#global data
	
	#print(data)
	
	#print(vectorName)
	
	if (vectorName == 'BallPositionR') and not invalid:                     # look for the BallPosition variable in the data stream#
		mmserver.sendVectorValue('ReturnedBallPositionR', vectorValue)      # echo back the value of BallPosition to #MotionMonitor
		mmserver.sendScalarValue('RCOUNT',RCOUNT)
		cursorR.setScale(0.1,vectorValue[2]*scalorxx,0.01250)#scale height according to step time in Z direction
		
		if (vectorValue[2] <= 0.1):
			HistBallR.setPosition([0.2, histR*scalorxx, 0])#update yellow history bar when HS happens
			steptimeR = histR
		else:
			histR = vectorValue[2]
			
		if (abs(steptimeR-targetR) <= targettol):#highlight the target when the target is hit
			gold = boxR.getColor(node = '')
			boxR.color( viz.WHITE )

		else:
			gold = boxR.getColor(node = '')
			boxR.color( viz.BLUE )
		
		if (vectorValue[0] < -20) & (Rforceold == 0.0) & (abs(steptimeR-targetR) <= targettol):
			RCOUNT = RCOUNT+1
			#rightcounter.setText(str(RCOUNT))
			rightcounter.message(str(RCOUNT))
		
		
		Rforceold = vectorValue[0]



		
	if (vectorName == 'BallPositionL') and not invalid:  
		mmserver.sendVectorValue('ReturnedBallPositionL', vectorValue)
		mmserver.sendScalarValue('LCOUNT',LCOUNT)
		cursorL.setScale(0.1,vectorValue[2]*scalorxx,0.01250)#scale cursor according to step time in Z direction
		
		if (vectorValue[2] <= 0.1):
			HistBallL.setPosition([-0.2, histL*scalorxx, 0])
			steptimeL = histL
		else:
			histL = vectorValue[2]
		
		if (abs(steptimeL-targetL) <= targettol):
			boxL.color( viz.WHITE )
		else:
			boxL.color( viz.BLUE )
			
		if (vectorValue[0] < -20) & (Lforceold == 0.0) & (abs(steptimeL-targetL) <= targettol):
			LCOUNT = LCOUNT+1
			#leftcounter.setText(str(LCOUNT))
			leftcounter.message(str(LCOUNT))
		
		
		Lforceold = vectorValue[0]
			
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
