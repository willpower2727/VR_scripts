from msvcrt import getch
import viz


viz.go()


def onKeyDown(key): 
    print key, ' is down.' 
    if key == viz.KEY_TAB: 
        print 'you hit the tab key' 
#Register the callback which to call the 'onKeyDown' function. 
viz.callback(viz.KEYDOWN_EVENT,onKeyDown)