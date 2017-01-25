# Test of exploding target animations

import viz
import vizact

viz.go()
global anim
anim = viz.addChild('ExT4.OSGB',scale=[1,1,1])

def start():
	global anim
	print('exploding...')
	anim.setAnimationState(0)
	
def stop():
	global anim
	print('stopped...')
	anim.setAnimationTime(0)
	anim.setAnimationState(-1)
	
	
viz.MainView.setPosition(0,0,-1.5)
	
vizact.onkeydown(' ',start)
vizact.onkeydown('s',stop)