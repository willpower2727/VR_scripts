"""
Key commands:
  1 - Raise/lower platform
  2 - Raise/lower pit
  Up Arrow - Zoom in video camera
  Down Arrow - Zoom out video camera
  Spacebar - Reset

Navigate using mouse + WASD keys
"""
import viz
import steve
import vizact
import vizcam
import imp
oculus = imp.load_source('oculus', 'C:\Program Files\WorldViz\Vizard5\python\oculus.py')
import vizlens
#import vizconnect

viz.setMultiSample(8)
#viz.fov(110)
viz.go(
#viz.FULLSCREEN
)

hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')
	
# Check if HMD supports position tracking
supportPositionTracking = hmd.getSensor().getSrcMask() & viz.LINK_POS
if supportPositionTracking:

	# Add camera bounds model
	camera_bounds = hmd.addCameraBounds()
	camera_bounds.visible(True)

	# Change color of bounds to reflect whether position was tracked
	def CheckPositionTracked():
		if hmd.getSensor().getStatus() & oculus.STATUS_POSITION_TRACKED:
			camera_bounds.color(viz.GREEN)
		else:
			camera_bounds.color(viz.RED)
	vizact.onupdate(0, CheckPositionTracked)

# Setup navigation node and link to main view
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())

# Apply user profile eye height to view
profile = hmd.getProfile()
if profile:
#	viewLink.setOffset([0,profile.eyeHeight,0])
	viewLink.setOffset([0,0,0.25])
else:
#	viewLink.setOffset([0,1.8,0])
	viewLink.setOffset([0,0,0])

viz.MainView.collision(viz.ON) 
viz.MainView.collisionBuffer(0.5)

#pincushion = vizlens.PincushionDistortion()
#pincushion.setK1(0.3)

# Simulate head tracker using keyboard/mouse navigator

#head_tracker = vizcam.addWalkNavigate()
#head_tracker = vizcam.addCameraTracker()
#head_tracker.setPosition([0,1.5,0])
#viz.mouse.setVisible(False)

# Add pit model
model = viz.add('pit.osgb')
model.setEuler(10,0,0)
#model.hint(viz.OPTIMIZE_INTERSECT_HINT)

# Get handle to platform object
platform = model.getChild('platform')
platform.raised = False
platform.positions = [[0,0,0],[0,7,0]]
platform.audio_start = viz.addAudio('sounds/platform_start.wav')
platform.audio_running = viz.addAudio('sounds/platform_running.wav',loop=True)
platform.audio_stop = viz.addAudio('sounds/platform_stop.wav')

def TogglePlatform():
	"""Toggle raising/lower of platform"""
	platform.raised = not platform.raised
	pos = platform.positions[platform.raised]
	platform.audio_start.stop()
	platform.audio_start.play()
	platform.audio_running.play()
	platform.runAction(vizact.moveTo(pos,speed=2.0))
	platform.addAction(vizact.call(platform.audio_stop.play))
	platform.addAction(vizact.call(platform.audio_running.pause))

vizact.onkeydown('1',TogglePlatform)

# Get handle to pit object
pit = model.getChild('pit')
pit.lowered = False
pit.positions = [[0,0,0],[0,-8.1,0]]
pit.colors = [viz.WHITE,viz.BLACK]
pit.audio_running = viz.addAudio('sounds/pit_running.wav',loop=True)
pit.audio_stop = viz.addAudio('sounds/pit_stop.wav')

# Use '2' key to raise/lower pit
def TogglePit():
	"""Toggle raising/lowering of pit"""
	pit.lowered = not pit.lowered
	pos = pit.positions[pit.lowered]
	pit.audio_running.play()
	pit.runAction(vizact.moveTo(pos,speed=2.0))
	pit.addAction(vizact.call(pit.audio_stop.play))
	pit.addAction(vizact.call(pit.audio_running.pause))

	# Use pit color to blend between lower/upper lightmaps
	duration = pit.getActionInstance().getDuration()
	color = pit.colors[pit.lowered]
	pit.runAction(vizact.fadeTo(color,time=duration),pool=1)

vizact.onkeydown('2',TogglePit)

# Create render texture for camera video feed
video = viz.addRenderTexture()

# Create render node for camera
cam = viz.addRenderNode()
cam.fov = 30.0
cam.setSize(1280,720)
cam.setInheritView(False)
cam.setPosition([-10.94835, 11.09378, 13.61334])
cam.setRenderTexture(video)
cam.setMultiSample(viz.AUTO_COMPUTE)
cam.setRenderLimit(viz.RENDER_LIMIT_FRAME)

# Get handle to screen object and apply video feed to it
screen = model.getChild('screen')
screen.texture(video)
cam.renderOnlyIfNodeVisible([screen])

# Use up/down keys to zoom camera in/out
def CameraZoom(inc):
	cam.fov = viz.clamp(cam.fov+inc,5.0,70.0)
	cam.setFov(cam.fov,1.77,0.1,1000)
vizact.whilekeydown(viz.KEY_UP,CameraZoom,vizact.elapsed(-20.0))
vizact.whilekeydown(viz.KEY_DOWN,CameraZoom,vizact.elapsed(20.0))
CameraZoom(0.0)

# Have camera always point towards view position
#def UpdateCamera():
#	cam.lookAt(viz.MainView.getPosition())
#vizact.ontimer(0,UpdateCamera)

# Add avatar to represent viewpoint
avatar = steve.Steve()
avatar.setTracker(viz.MainView)
avatar.disable(viz.INTERSECTION)

# Only render avatar for camera
avatar.renderOnlyToRenderNodes([cam],excludeMainPass=True)

# Add fall sound
fallSound = viz.addAudio('sounds/pit_fall.wav')

# Add blur effect for fall action
import vizfx.postprocess
from vizfx.postprocess.blur import DirectionalBlurEffect
blurEffect = DirectionalBlurEffect(samples=3,angle=90)
vizfx.postprocess.addEffect(blurEffect)

# Add red quad to flash screen after falling
flash_quad = viz.addTexQuad(parent=viz.ORTHO)
flash_quad.color(viz.RED)
flash_quad.alignment(viz.ALIGN_LEFT_BOTTOM)
flash_quad.blendFunc(viz.GL_ONE,viz.GL_ONE)
flash_quad.visible(False)
viz.link(viz.MainWindow.WindowSize,flash_quad,mask=viz.LINK_SCALE)

def FallAction():
	"""Flashes screen red and animates blur effect"""
	fallSound.stop()
	fallSound.play()
	flash_quad.visible(True)
	flash_quad.color(viz.RED)
	fade_out = vizact.fadeTo(viz.BLACK,time=2.5)
	flash_quad.runAction(vizact.sequence(fade_out,vizact.method.visible(False)))
	flash_quad.runAction(vizact.call(blurEffect.setDistance,vizact.mix(50,0,time=2.5)),pool=1)

class TrackedFaller(viz.VizNode):
	"""Class for simulating a head tracked user falling"""

	# Threshold to clamp height to ground level
	GROUND_CLAMP_THRESHOLD = 0.1

	# Distance from edge to allow before falling
	FALL_EDGE_BUFFER = 0.4

	# Maximum step height allowed
	STEP_HEIGHT = 0.3

	# Maximum fall velocity
	TERMINAL_VELOCITY = 60.0

	# Gravity acceleration
	GRAVITY = 9.8

	def __init__(self,tracker):

		# Initialize using group node
		group = viz.addGroup()
		viz.VizNode.__init__(self,group.id)

		self._offset = viz.Vector()
		self._tracker = tracker
		self._velocity = 0.0

		# Update tracker every frame
		self._updater = vizact.onupdate(0,self.update)

	def _onFinishedFalling(self):
		pass

	def _intersect(self,begin,end):
		return viz.intersect(begin,end)

	def _clearVelocity(self):
		if self._velocity > 0.0:
			self._onFinishedFalling()
			self._velocity = 0.0

	def reset(self):
		"""Reset faller to origin"""
		self.setOffset([0,0,0])
		self._velocity = 0.0

	def setOffset(self, offset):
		"""Set offset"""
		self._offset.set(offset)
		self.setPosition(self._offset+self._tracker.getPosition())

	def getOffset(self):
		"""Get offset"""
		return list(self._offset)

	def getVelocity(self):
		return self._velocity

	def update(self):

		# Get tracker position
		tracker_pos = self._tracker.getPosition()

		# Get current view position
		view_pos = self._offset + tracker_pos
		view_pos[1] =  self._offset[1] + self.STEP_HEIGHT

		# Perform intersection to determine height of view above ground
		line_end = view_pos - [0,500,0]
		isections = [self._intersect(view_pos,line_end)]

		# Check points around position to allow buffer around edges
		if self.FALL_EDGE_BUFFER > 0.0:
			buf = self.FALL_EDGE_BUFFER
			isections.append(self._intersect(view_pos+[buf,0,0],line_end+[buf,0,0]))
			isections.append(self._intersect(view_pos+[-buf,0,0],line_end+[-buf,0,0]))
			isections.append(self._intersect(view_pos+[0,0,buf],line_end+[0,0,buf]))
			isections.append(self._intersect(view_pos+[0,0,-buf],line_end+[0,0,-buf]))

		# Get intersection with largest height
		try:
			info = max((info for info in isections if info.valid),key=lambda info:info.point[1])
		except ValueError:
			info = isections[0]

		if info.valid:

			# Get height above ground
			ground_height = info.point[1]

			# If current offset is greater than ground height, then apply gravity
			if self._offset[1] > ground_height:
				dt = viz.getFrameElapsed()
				self._velocity = min(self._velocity + (self.GRAVITY * dt),self.TERMINAL_VELOCITY)
				self._offset[1] -= (self._velocity * dt)

			# Clamp to ground level if fallen below threshold
			if self._offset[1] - self.GROUND_CLAMP_THRESHOLD < ground_height:
				self._offset[1] = ground_height
				self._clearVelocity()

		# Update position/orientation
		self.setPosition(self._offset+tracker_pos)
		self.setQuat(self._tracker.getQuat())

class PitTrackedFaller(TrackedFaller):
	"""Derived tracked faller class for performing action when finished falling"""
	def _onFinishedFalling(self):
		if self.getVelocity() > 6.0:
			FallAction()

# Create tracked faller and link to main view
faller = PitTrackedFaller(head_tracker)
viz.link(faller,viz.MainView)

def Reset():
	"""Reset platforms and place faller back at origin"""

	# Reset platform
	platform.clearActions(viz.ALL_POOLS)
	platform.raised = False
	platform.setPosition([0,0,0])
	platform.audio_running.pause()

	# Reset pit
	pit.clearActions(viz.ALL_POOLS)
	pit.lowered = False
	pit.setPosition([0,0,0])
	pit.color(viz.WHITE)
	pit.audio_running.pause()

	# Reset faller
	faller.reset()

vizact.onkeydown(' ',Reset)
