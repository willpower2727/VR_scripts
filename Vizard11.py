import viz
import vizinfo
import vizact
import time
import viztask

viz.go()
#set target tolerance for stride length
global targetL
targetL = 0.3

global targetR
targetR = 0.3

global targettol
targettol = 0.05

global boxL
boxL = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxL.setPosition([-0.2,targetL,0])
#boxL.visible(0)
global boxR
boxR = viz.addChild('target2.obj',color=(0.063,0.102,0.898),scale=[0.1,(targettol+0.02),0.0125])
boxR.setPosition([0.2,targetR,0])

viz.MainView.setPosition(0, 0.25, -1.25)
viz.MainView.setEuler(0,0,0)


def nothing():

		yield viztask.waitKeyDown(' ')
		boxL.visible(0)
		stuff = viz.addChild('targetexplode12.osgb',pos=[-0.2,targetL,0],scale=[0.1,(targettol+0.02),0.0125])
#		stuff = viz.addChild('targetexplode10.osgb',pos=[0,2,20])
		stuff.setAnimationState(0)
		
viztask.schedule( nothing() )

def somethingelse():
	
	yield viztask.waitKeyDown('s')
	boxL.visible(1)
#	stuff.remove()
	
viztask.schedule( somethingelse() )
	
def froo():

		yield viztask.waitKeyDown('k')
		boxL.visible(0)
		stuff = viz.addChild('targetexplode12.osgb',pos=[-0.2,targetL,0],scale=[0.1,(targettol+0.02),0.0125])
#		stuff = viz.addChild('targetexplode10.osgb',pos=[0,2,20])
		stuff.setAnimationState(0)
		
viztask.schedule( froo() )
	
	
	
	
	