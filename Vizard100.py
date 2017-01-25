import viz
import time

viz.splashScreen('C:\Users\Gelsey Torres-Oviedo\Desktop\VizardFolderVRServer\Logo_final.jpg')
viz.go(
viz.FULLSCREEN
)

#set target tolerance for stride length
global targetL
targetL = 0.5
time.sleep(3)
global targetR
targetR = 0.5 

global targettol
targettol = 0.025

global boxL
boxL = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.005])
boxL.setPosition([-0.2,targetL,0])

global boxR
boxR = viz.addChild('target.obj',color=(0.063,0.102,0.898),scale=[0.1,targettol,0.005])
boxR.setPosition([0.2,targetR,0])

viz.MainView.setPosition(0, 0.4, -1.25)
viz.MainView.setEuler(0,0,0)