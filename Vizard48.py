import vizact
import viz

def whattodo(biggle):
	print('you are a pirate')
	
viz.go()

vizact.onkeydown('65365',whattodo,'')


def onKeyDown(key): 
    print key, ' is down.' 
    if key == viz.KEY_TAB: 
        print 'you hit the tab key' 
#Register the callback which to call the 'onKeyDown' function. 
viz.callback(viz.KEYDOWN_EVENT,onKeyDown)