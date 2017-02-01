<<<<<<< HEAD
﻿""" Optical Flow Rev3

Visual flow at a set speed, no head tracking, 

#Use with V2P DK2 R2
wda 1/9/2017
"""
import viz
import vizshape
import time
import vizinfo
import random
import itertools
import socket
import sys
import io
import re
import csv
import threading
import Queue
import time
import vizact
import struct
import array
import math
import vizlens
import oculus
import subprocess
import vizfx

#global cpps
#cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe"')
#time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
viz.go(
#viz.FULLSCREEN #run world in full screen
)

monoWindow = viz.addWindow(size=(1,1), pos=(0,1), scene=viz.addScene())
monoQuad = viz.addTexQuad(parent=viz.ORTHO, scene=monoWindow)
monoQuad.setBoxTransform(viz.BOX_ENABLED)
monoQuad.setTexQuadDisplayMode(viz.TEXQUAD_FILL)
texture = vizfx.postprocess.getEffectManager().getColorTexture()

def UpdateTexture():
    monoQuad.texture(texture)
vizact.onupdate(0, UpdateTexture)



global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor()
#profile = hmd.getProfile()
#hmd.setIPD(profile.ipd)


OF1 = viz.addChild('OpticFlowBox5.osgb',scale=[3,3,3])
OF1.disable(viz.LIGHTING)
OF2 = viz.addChild('OpticFlowBox5.osgb',scale=[3,3,3])
OF2.disable(viz.LIGHTING)
OF2.setPosition(0,0,1.27*3)
OF3 = viz.addChild('OpticFlowBox5.osgb',scale=[3,3,3])
OF3.disable(viz.LIGHTING)
OF3.setPosition(0,0,1.27*6)

viz.MainView.setPosition(0,0.15,-1.27*3/2+0.002)
viz.MainView.setEuler(0,0,0)


#def startmoving(biggle):
global endflag
endflag = threading.Event()

def thread1():
	global endflag
	view = viz.MainView
	while not endflag.is_set():
		out = view.getPosition(mode=viz.ABS_GLOBAL)
#		print('x: ',out)

		if (out[2] > 1.27*3/2):
#			view.velocity(0,0,0)
			view.setPosition(0,0.15,-1.27*3/2+0.002)
#			OF1.setPosition(0,0,1.27*9)
#			print('OF moved')
	print('thread terminated')

def raisestop(biggle):
	global endflag
	endflag.set()
	viz.quit()

t1 = threading.Thread(target=thread1)
t1.start()
vizact.onkeydown('s', viz.MainView.velocity, [0,0,1 ]  )
vizact.onupdate(0, UpdateTexture)
vizact.onkeydown('q',raisestop,'biggle')
=======
﻿""" Optical Flow Rev3

Visual flow at a set speed, no head tracking, 

#Use with V2P DK2 R2
wda 1/9/2017
"""
import viz
import vizshape
import time
import vizinfo
import random
import itertools
import socket
import sys
import io
import re
import csv
import threading
import Queue
import time
import vizact
import struct
import array
import math
import vizlens
import oculus
import subprocess
import vizfx

#global cpps
#cpps = subprocess.Popen('"C:/Users/Gelsey Torres-Oviedo/Documents/Visual Studio 2013/Projects/Vicon2Python_DK2_rev2/x64/Release/Vicon2Python_DK2_rev2.exe"')
#time.sleep(3)

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final_DK2.jpg')
viz.setMultiSample(8)
viz.go(
#viz.FULLSCREEN #run world in full screen
)

monoWindow = viz.addWindow(size=(1,1), pos=(0,1), scene=viz.addScene())
monoQuad = viz.addTexQuad(parent=viz.ORTHO, scene=monoWindow)
monoQuad.setBoxTransform(viz.BOX_ENABLED)
monoQuad.setTexQuadDisplayMode(viz.TEXQUAD_FILL)
texture = vizfx.postprocess.getEffectManager().getColorTexture()

def UpdateTexture():
    monoQuad.texture(texture)
vizact.onupdate(0, UpdateTexture)



global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor()
#profile = hmd.getProfile()
#hmd.setIPD(profile.ipd)


OF1 = viz.addChild('OpticFlowBox3.osgb',scale=[3,3,3])
OF1.disable(viz.LIGHTING)
OF2 = viz.addChild('OpticFlowBox3.osgb',scale=[3,3,3])
OF2.disable(viz.LIGHTING)
OF2.setPosition(0,0,1.27*3)
OF3 = viz.addChild('OpticFlowBox3.osgb',scale=[3,3,3])
OF3.disable(viz.LIGHTING)
OF3.setPosition(0,0,1.27*6)

viz.MainView.setPosition(0,0.15,-1.27*3/2+0.002)
viz.MainView.setEuler(0,0,0)


#def startmoving(biggle):
global endflag
endflag = threading.Event()

def thread1():
	global endflag
	view = viz.MainView
	while not endflag.is_set():
		out = view.getPosition(mode=viz.ABS_GLOBAL)
#		print('x: ',out)

		if (out[2] > 1.27*3/2):
#			view.velocity(0,0,0)
			view.setPosition(0,0.15,-1.27*3/2+0.002)
#			OF1.setPosition(0,0,1.27*9)
#			print('OF moved')
	print('thread terminated')

def raisestop(biggle):
	global endflag
	endflag.set()
	viz.quit()

t1 = threading.Thread(target=thread1)
t1.start()
vizact.onkeydown('s', viz.MainView.velocity, [0,0,0.4 ]  )
vizact.onupdate(0, UpdateTexture)
vizact.onkeydown('q',raisestop,'biggle')
>>>>>>> origin/master
