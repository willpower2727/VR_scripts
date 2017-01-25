#script that starts the vizard enviroment and displays the origin and coordinate axes
#WDA 3/14/2016

import viz
import vizshape

viz.go(

)

origin = vizshape.addSphere(.01,50,50)
origin.color(1,1,0)
origin.setPosition(0,0,0)

viz.startLayer(viz.LINES) 
viz.vertex(0,0,0) #Vertices are split into pairs. 
viz.vertex(1,0,0) 
myLines = viz.endLayer()
myLines.color(1,0,0)
messagewinx = viz.addText('X',pos=[1,0,0],scale=[0.04,0.04,0.04])

viz.startLayer(viz.LINES) 
viz.vertex(0,0,0) #Vertices are split into pairs. 
viz.vertex(0,1,0) 
myLines2 = viz.endLayer()
myLines2.color(0,1,0)
messagewiny = viz.addText('Y',pos=[0,1,0],scale=[0.04,0.04,0.04])

viz.startLayer(viz.LINES) 
viz.vertex(0,0,0) #Vertices are split into pairs. 
viz.vertex(0,0,1) 
myLines3 = viz.endLayer()
myLines3.color(0,0,1)
messagewinz = viz.addText('Z',pos=[0,0,1],scale=[0.04,0.04,0.04])

viz.startLayer(viz.LINES) 
viz.vertex(0,0,0) #Vertices are split into pairs. 
viz.vertex(0.8,0,0) 
myLines4 = viz.endLayer()
myLines4.color(1,1,1)
myLines4.setEuler(45,0,0)

viz.MainView.setPosition(0.6,0.5,-1.5)
viz.MainView.setEuler(-10,0,0)