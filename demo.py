<<<<<<< HEAD
﻿""" Test script for the animator using a vicon system

when calibrating:
	press c to calibrate the avatar (applies a t-pose reset and scales the avatar model to the height of the user)
	press s to save the scale and t-pose calibration

when running a different set of data or later configuration press 'l' to load the previously stored t-pose calibration
"""


import viz
import vizshape


HEAD_OFFSET = [0, -0.04, 0.11]#0cm left/right 4cm down 11cm forward 
HEAD_TRACKER_NAME = 'head'
RHAND_TRACKER_NAME = 'rhand'
LHAND_TRACKER_NAME = 'lhand'
RFOOT_TRACKER_NAME = 'rfoot'
LFOOT_TRACKER_NAME = 'lfoot'
WAIST_TRACKER_NAME = 'waist'



viz.go()

# code to add the grid to the environment
grid = vizshape.addGrid()

# code to add the trackers
vrpn = viz.add('vrpn7.dle')

def addViconTracker(name):
	tracker = vrpn.addTracker( name+'@localhost' )
	tracker.swapPos( [-2,3,1] )
	tracker.swapQuat( [2,-3,-1,4] )
	if name != HEAD_TRACKER_NAME:
		obj = vizshape.addAxes(.3 )
		objLink = viz.link( tracker, obj )
	return tracker

head = addViconTracker(HEAD_TRACKER_NAME)
head = viz.link(head, viz.NullLinkable)
head.preTrans(HEAD_OFFSET)
obj = vizshape.addAxes(.1 )
objLink = viz.link( head, obj )

rhand = addViconTracker(RHAND_TRACKER_NAME)
lhand = addViconTracker(LHAND_TRACKER_NAME)
rfoot = addViconTracker(RFOOT_TRACKER_NAME)
lfoot = addViconTracker(LFOOT_TRACKER_NAME)
waist = addViconTracker(WAIST_TRACKER_NAME)

# initialization code for avatar which is a CompleteCharactersMale
avatar = viz.add('vcc_male.cfg')

# need to get the raw tracker dict for animating the avatars
from avatar_animation import animator
from avatar_animation import skeleton

# initialize animator for avatar
avatarSkeleton = skeleton.CompleteCharactersSkeleton(avatar)

# list of what trackers are assigned to what body part, 
# format is: (name of bone, parent, tracker, degrees of freedom used)
trackerAssignmentList = [
	('head', 'none', head, animator.DOF_6DOF),
	('lhand', 'none', lhand, animator.DOF_6DOF),
	('rhand', 'none', rhand, animator.DOF_6DOF),
#	('relbow', 'none', relbow, animator.DOF_6DOF),
#	('lelbow', 'none', lelbow, animator.DOF_6DOF),
	('lfoot', 'none', lfoot, animator.DOF_6DOF),
	('rfoot', 'none', rfoot, animator.DOF_6DOF),
	('waist', 'none', waist, animator.DOF_6DOF),
]
#animator = animator.UpperBody(avatar, avatarSkeleton, trackerAssignmentList)
#animator = animator.HeadArmsAndLegs(avatar, avatarSkeleton, trackerAssignmentList)
animator = animator.SixPoint(avatar, avatarSkeleton, trackerAssignmentList)
#animator.setScale([1.3]*3)

def calibrate():
	animator.autoScaleAvatar()
	animator.tposeReset()

vizact.onkeydown('c', calibrate)
#vizact.onkeydown('1', animator.autoScaleAvatar)
#vizact.onkeydown('2', animator.tposeReset)


def saveCalibration():
	data = animator.getCalibrationData()
	print data.scale
	print data._headSlotShift
	print data._postHeadSlotShift
	import pickle
	with open('calibration.acd', 'wb') as file:
		pickle.dump(data, file)


def loadCalibration():
	import pickle
	with open('calibration.acd', 'rb') as file:
		data = pickle.load(file)
	animator.setCalibrationData(data)


vizact.onkeydown('s', saveCalibration)
vizact.onkeydown('l', loadCalibration)


def initExtraWindows():
	# initialization code for ortho which is a GenericOrtho
	mask=viz.ALLCLIENTS
	stereo=viz.OFF
	fullscreen=viz.OFF
	bottom=-2
	top=2
	left=-2
	right=2
	near=0.1
	far=100
	newWindow = viz.addWindow()
	newView = viz.addView()
	newWindow.setView(newView)
	# aligned to top left
	newWindow.setPosition(0, 1)
	newWindow.setSize(0.3, 0.3)
	
	if mask != viz.ALLCLIENTS:
		viz.cluster.setMask(viz.ALLCLIENTS & ~mask)
		newWindow.visible(False)
		viz.cluster.setMask(viz.ALLCLIENTS)
	newWindow.ortho(bottom,top,left,right,near,far)
	viz.window.setFullscreen(mode=fullscreen)
	newWindow.stereo(stereo)
	newView.setPosition(0, 1, 3)
	newView.setEuler(180, 0, 0)
	
	# initialization code for ortho2 which is a GenericOrtho
	mask=viz.ALLCLIENTS
	stereo=viz.OFF
	fullscreen=viz.OFF
	bottom=-2
	top=2
	left=-2
	right=2
	near=0.1
	far=100
	newWindow = viz.addWindow()
	newView = viz.addView()
	newWindow.setView(newView)
	# aligned to bottom left
	newWindow.setPosition(0, 0.3)
	newWindow.setSize(0.3, 0.3)
	if mask != viz.ALLCLIENTS:
		viz.cluster.setMask(viz.ALLCLIENTS & ~mask)
		newWindow.visible(False)
		viz.cluster.setMask(viz.ALLCLIENTS)
	newWindow.ortho(bottom,top,left,right,near,far)
	viz.window.setFullscreen(mode=fullscreen)
	newWindow.stereo(stereo)
	newView.setPosition(0, 3, 0)
	newView.setEuler(0, 90, 0)

initExtraWindows()

viz.MainView.setPosition(0, 1.6, 5)
viz.MainView.setEuler(180,0,0)







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
ball = viz.add('sphere.x', color=viz.PURPLE, scale=[0.1,0.1,0.1], cache=viz.CACHE_NONE)

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
def onCalibrationFileGenerated(calibrationFileName):
	print 'Calibration file generated.'
	import pickle
	with open(calibrationFileName, 'rb') as file:
		data = pickle.load(file)      # load the data from the calibration file
	animator.setCalibrationData(data) # send the calibration data to the animator module... this should make the avatar's segments snap into their correct positions
viz.callback(mmserver.CALIBRATION_FILE_GENERATED_EVENT, onCalibrationFileGenerated)

# Register callback for our "scalar value received" event.
def onScalarValueReceived(scalarName, scalarValue, invalid):
	return # currently, do nothing
viz.callback(mmserver.SCALAR_VALUE_RECEIVED_EVENT, onScalarValueReceived)

# Register callback for our "vector value received" event.
def onVectorValueReceived(vectorName, vectorValue, invalid):
	global ball
	if (vectorName == 'BallPosition') and not invalid:                     # look for the BallPosition variable in the data stream
		mmserver.sendVectorValue('ReturnedBallPosition', vectorValue)      # echo back the value of BallPosition to MotionMonitor
		ball.setPosition(- vectorValue[1], vectorValue[2], vectorValue[0]) # use the value of BallPosition to place our purple ball - but change the vector to match the rearranged world axes (see line 35)
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
=======
﻿""" Test script for the animator using a vicon system

when calibrating:
	press c to calibrate the avatar (applies a t-pose reset and scales the avatar model to the height of the user)
	press s to save the scale and t-pose calibration

when running a different set of data or later configuration press 'l' to load the previously stored t-pose calibration
"""


import viz
import vizshape


HEAD_OFFSET = [0, -0.04, 0.11]#0cm left/right 4cm down 11cm forward 
HEAD_TRACKER_NAME = 'head'
RHAND_TRACKER_NAME = 'rhand'
LHAND_TRACKER_NAME = 'lhand'
RFOOT_TRACKER_NAME = 'rfoot'
LFOOT_TRACKER_NAME = 'lfoot'
WAIST_TRACKER_NAME = 'waist'



viz.go()

# code to add the grid to the environment
grid = vizshape.addGrid()

# code to add the trackers
vrpn = viz.add('vrpn7.dle')

def addViconTracker(name):
	tracker = vrpn.addTracker( name+'@localhost' )
	tracker.swapPos( [-2,3,1] )
	tracker.swapQuat( [2,-3,-1,4] )
	if name != HEAD_TRACKER_NAME:
		obj = vizshape.addAxes(.3 )
		objLink = viz.link( tracker, obj )
	return tracker

head = addViconTracker(HEAD_TRACKER_NAME)
head = viz.link(head, viz.NullLinkable)
head.preTrans(HEAD_OFFSET)
obj = vizshape.addAxes(.1 )
objLink = viz.link( head, obj )

rhand = addViconTracker(RHAND_TRACKER_NAME)
lhand = addViconTracker(LHAND_TRACKER_NAME)
rfoot = addViconTracker(RFOOT_TRACKER_NAME)
lfoot = addViconTracker(LFOOT_TRACKER_NAME)
waist = addViconTracker(WAIST_TRACKER_NAME)

# initialization code for avatar which is a CompleteCharactersMale
avatar = viz.add('vcc_male.cfg')

# need to get the raw tracker dict for animating the avatars
from avatar_animation import animator
from avatar_animation import skeleton

# initialize animator for avatar
avatarSkeleton = skeleton.CompleteCharactersSkeleton(avatar)

# list of what trackers are assigned to what body part, 
# format is: (name of bone, parent, tracker, degrees of freedom used)
trackerAssignmentList = [
	('head', 'none', head, animator.DOF_6DOF),
	('lhand', 'none', lhand, animator.DOF_6DOF),
	('rhand', 'none', rhand, animator.DOF_6DOF),
#	('relbow', 'none', relbow, animator.DOF_6DOF),
#	('lelbow', 'none', lelbow, animator.DOF_6DOF),
	('lfoot', 'none', lfoot, animator.DOF_6DOF),
	('rfoot', 'none', rfoot, animator.DOF_6DOF),
	('waist', 'none', waist, animator.DOF_6DOF),
]
#animator = animator.UpperBody(avatar, avatarSkeleton, trackerAssignmentList)
#animator = animator.HeadArmsAndLegs(avatar, avatarSkeleton, trackerAssignmentList)
animator = animator.SixPoint(avatar, avatarSkeleton, trackerAssignmentList)
#animator.setScale([1.3]*3)

def calibrate():
	animator.autoScaleAvatar()
	animator.tposeReset()

vizact.onkeydown('c', calibrate)
#vizact.onkeydown('1', animator.autoScaleAvatar)
#vizact.onkeydown('2', animator.tposeReset)


def saveCalibration():
	data = animator.getCalibrationData()
	print data.scale
	print data._headSlotShift
	print data._postHeadSlotShift
	import pickle
	with open('calibration.acd', 'wb') as file:
		pickle.dump(data, file)


def loadCalibration():
	import pickle
	with open('calibration.acd', 'rb') as file:
		data = pickle.load(file)
	animator.setCalibrationData(data)


vizact.onkeydown('s', saveCalibration)
vizact.onkeydown('l', loadCalibration)


def initExtraWindows():
	# initialization code for ortho which is a GenericOrtho
	mask=viz.ALLCLIENTS
	stereo=viz.OFF
	fullscreen=viz.OFF
	bottom=-2
	top=2
	left=-2
	right=2
	near=0.1
	far=100
	newWindow = viz.addWindow()
	newView = viz.addView()
	newWindow.setView(newView)
	# aligned to top left
	newWindow.setPosition(0, 1)
	newWindow.setSize(0.3, 0.3)
	
	if mask != viz.ALLCLIENTS:
		viz.cluster.setMask(viz.ALLCLIENTS & ~mask)
		newWindow.visible(False)
		viz.cluster.setMask(viz.ALLCLIENTS)
	newWindow.ortho(bottom,top,left,right,near,far)
	viz.window.setFullscreen(mode=fullscreen)
	newWindow.stereo(stereo)
	newView.setPosition(0, 1, 3)
	newView.setEuler(180, 0, 0)
	
	# initialization code for ortho2 which is a GenericOrtho
	mask=viz.ALLCLIENTS
	stereo=viz.OFF
	fullscreen=viz.OFF
	bottom=-2
	top=2
	left=-2
	right=2
	near=0.1
	far=100
	newWindow = viz.addWindow()
	newView = viz.addView()
	newWindow.setView(newView)
	# aligned to bottom left
	newWindow.setPosition(0, 0.3)
	newWindow.setSize(0.3, 0.3)
	if mask != viz.ALLCLIENTS:
		viz.cluster.setMask(viz.ALLCLIENTS & ~mask)
		newWindow.visible(False)
		viz.cluster.setMask(viz.ALLCLIENTS)
	newWindow.ortho(bottom,top,left,right,near,far)
	viz.window.setFullscreen(mode=fullscreen)
	newWindow.stereo(stereo)
	newView.setPosition(0, 3, 0)
	newView.setEuler(0, 90, 0)

initExtraWindows()

viz.MainView.setPosition(0, 1.6, 5)
viz.MainView.setEuler(180,0,0)







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
ball = viz.add('sphere.x', color=viz.PURPLE, scale=[0.1,0.1,0.1], cache=viz.CACHE_NONE)

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
def onCalibrationFileGenerated(calibrationFileName):
	print 'Calibration file generated.'
	import pickle
	with open(calibrationFileName, 'rb') as file:
		data = pickle.load(file)      # load the data from the calibration file
	animator.setCalibrationData(data) # send the calibration data to the animator module... this should make the avatar's segments snap into their correct positions
viz.callback(mmserver.CALIBRATION_FILE_GENERATED_EVENT, onCalibrationFileGenerated)

# Register callback for our "scalar value received" event.
def onScalarValueReceived(scalarName, scalarValue, invalid):
	return # currently, do nothing
viz.callback(mmserver.SCALAR_VALUE_RECEIVED_EVENT, onScalarValueReceived)

# Register callback for our "vector value received" event.
def onVectorValueReceived(vectorName, vectorValue, invalid):
	global ball
	if (vectorName == 'BallPosition') and not invalid:                     # look for the BallPosition variable in the data stream
		mmserver.sendVectorValue('ReturnedBallPosition', vectorValue)      # echo back the value of BallPosition to MotionMonitor
		ball.setPosition(- vectorValue[1], vectorValue[2], vectorValue[0]) # use the value of BallPosition to place our purple ball - but change the vector to match the rearranged world axes (see line 35)
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
>>>>>>> origin/master
