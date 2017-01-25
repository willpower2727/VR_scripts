# Test of exploding fire

import viz
import vizact

viz.go()
box1 = viz.addChild('ExT1.osgb',pos=[0,0,0],scale=[.2,.2,.2])
box1.setAnimationTime(0)

global fire
fire = viz.addChild('fire2.OSG',scale=[2,2,2])
#fire.hasparticles()
fire.setEuler(0,90,0)
#fire.visible(0)
viz.phys.enable()
viz.phys.setGravity(0,0,0)
firep = fire.collideSphere()
#fire.applyForce( dir=[0,0,-10000],duration=2)

def spin():
	print('rescale and spin')
#	fire.addAction(vizact.spin(1,0,0,180,viz.FOREVER))
	fire.setEuler(0,270,0)
	fire.setScale([1,1,1])
	fire.setPosition(0,0,0)

def hide(nothing):
	box1.visible(0)
	fire.visible(0)
	
def explode():
	print('apply spin')
#	fire.setPosition(0,0,0)
#	fire.applyForce( dir=[0,0,-0.01],duration=0.001)
#	fire.addAction(vizact.spin(1,1,0,500,viz.FOREVER))
#	fire.setScale([2,2,2])
#	fire.setScale([4,4,4])
#	fire.setAnimationSpeed(20)
	box1.visible(1)
	box1.setAnimationTime(0)
	box1.setAnimationState(0)
	fire.visible(1)
	vizact.ontimer2(0.6,0,hide,0)
	
	
	
viz.MainView.setPosition(0,0,-1.5)
#	
vizact.onkeydown(' ',spin)
vizact.onkeydown('s',explode)
