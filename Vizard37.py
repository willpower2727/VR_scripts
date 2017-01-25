import viz
import vizshape


viz.go(
viz.FULLSCREEN
)

#h = vizshape.addSphere(0.125,20,20)
h = vizshape.addQuad(size=[1,1])
h.setParent(viz.SCREEN)
h.setPosition(0.5,0.5,0)
#h = viz.addChild('ball.wrl')
#h = viz.addChild('hidesphere.wrl',scale=[0.1,0.1,0.1])
h.color(1,1,1)
h.disable(viz.LIGHTING)

viz.MainView.setPosition(0,0,-1)
