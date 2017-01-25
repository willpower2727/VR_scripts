import viz
import vizact
import vizshape

viz.go()

VRPN_SOURCE = 'Tracker0@127.0.0.1'
#VRPN_SOURCE = 'Nexus@localhost'

viz.move([0,-1,-5])

axes = vizshape.addAxes(length=0.5)

vrpn = viz.add('vrpn7.dle')
headtracker = vrpn.addTracker(VRPN_SOURCE)
headtracker.swapPos([-1,3,-2])

#viz.link(headtracker,axes)

def showData():
	print('position')
	print headtracker.getPosition()
#	print headtracker.getEuler()
	
vizact.ontimer(1,showData)