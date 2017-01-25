import viz
import vizinfo
import vizact

viz.go()

#Add an InfoPanel with a title bar
#viz.MainView.setPosition(0, 0, -2)
#viz.MainView.setEuler(0,0,0)
#video = viz.addTexQuad()

video = viz.addVideo('RightSuccess0001-0040.avi')

#rightplane.texture(rightblast)
#rightblast.play()

#object = viz.add('cylinder.wrl') 
#object.texture(rightblast)
#dojo = viz.addChild('dojo.osgb')

#video = viz.addVideo('vizard.mpg')


#quad = viz.addTexQuad(parent=viz.ORTHO, scale=[1000,1000,0])
#quad.texture(video)
#viz.link(viz.MainWindow.RightTop,quad,offset=(-50,-50,0))

movingQuad = viz.addTexQuad(pos=[0,1.8,2],scale = [1,1,0])
movingQuad.texture(video)
video.loop()
video.play()
#movingQuad.runAction(vizact.move(0,0,1,time=6))