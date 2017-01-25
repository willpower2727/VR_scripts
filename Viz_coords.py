import viz
import vizshape

viz.startLayer(viz.LINES)
viz.vertexColor(viz.YELLOW)
viz.vertex(0,0,0)
viz.vertex(1,0,0)
X = viz.endLayer()

viz.startLayer(viz.LINES)
viz.vertex(0,0,0)
viz.vertex(0,1,0)
Y = viz.endLayer()

viz.startLayer(viz.LINES)
viz.vertexColor(viz.BLUE)
viz.vertex(0,0,0)
viz.vertex(0,0,1)
Z = viz.endLayer()

viz.go()

viz.MainView.setPosition(0,0,-1)