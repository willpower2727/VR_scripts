

import viz
import vizshape

viz.go(

viz.FULLSCREEN
)



#viz.MainView.setPosition(0, 0, -1)
#viz.MainView.setEuler(0,0,0)

#setup a variable to scale the height of objects so that the screen setup is optimized for viewing base on target values
global scalorxx
scalorxx = 0.6667

#set target tolerance for step time
global targetL
targetL = 1

global targetR
targetR = 1

global targettol
targettol = 0.05

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol*0.5,0.0125])
boxL.setPosition([-0.2,(targetL-targettol)*scalorxx,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol*0.5,0.0125])
boxR.setPosition([0.2,(targetR-targettol)*scalorxx,0])

global boxPELVIS  #stationar box that represents where the centroid of the pelvis markers is located
boxPELVIS = viz.addChild('box.wrl',color=viz.PURPLE)
boxPELVIS.setPosition([0,0,0])
boxPELVIS.setScale([0.05,0.01,0.05])

viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)