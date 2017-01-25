#test script for loading optic flow osgb from 3ds

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
import imp
oculus = imp.load_source('oculus', 'C:\Program Files\WorldViz\Vizard5\python\oculus.py')
import subprocess
import vizfx

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

global hmd
view = viz.addView
hmd = oculus.Rift()
hmd.getSensor()

viz.MainView.setPosition(0,0.15,-1.27*3/2+0.002)
viz.MainView.setEuler(0,0,0)

OF1 = viz.addChild('OpticFlowBox3.osgb',scale=[3,3,3])
OF1.disable(viz.LIGHTING)
OF2 = viz.addChild('OpticFlowBox3.osgb',scale=[3,3,3])
OF2.disable(viz.LIGHTING)
OF2.setPosition(0,0,1.27*3)
OF3 = viz.addChild('OpticFlowBox3.osgb',scale=[3,3,3])
OF3.disable(viz.LIGHTING)
OF3.setPosition(0,0,1.27*6)

#quad = vizshape.addQuad(size=(1,1),axis=vizshape.AXIS_Z)

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