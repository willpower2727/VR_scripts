import viz
import vizinfo

viz.go(
viz.FULLSCREEN
)
viz.visible(1)
#Add an InfoPanel with a title bar
waitpanel = vizinfo.InfoPanel('Hello \nWorld',align=viz.ALIGN_CENTER_TOP,fontSize=75,icon=False,key=None)
viz.MainView.setPosition(0, 0.5, -1.5)
viz.MainView.setEuler(0,0,0)
#HistBallL = viz.add('dojo.osgb')