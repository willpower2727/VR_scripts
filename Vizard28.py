#import viz
#
#viz.go()
#
#h = viz.getCurrentEvent()
#print(h)
import win32gui, win32con, win32api
import time

def OnPaint(hwnd, msg, wp, lp):
    """Windows needs repainting"""
    
    dc, ps=win32gui.BeginPaint(hwnd)
    
    #Draw red circle
    br=win32gui.CreateSolidBrush(win32api.RGB(255,0,0))
    win32gui.SelectObject(dc, br)
    win32gui.Ellipse(dc, 20,20,120,120)
    
    #Draw green rectangle
    br=win32gui.CreateSolidBrush(win32api.RGB(0,255,0))
    win32gui.SelectObject(dc, br)
    win32gui.Rectangle(dc, 150,20,300,120)
    
    #Draw blue triangle
    br=win32gui.CreateSolidBrush(win32api.RGB(0,0,255))
    win32gui.SelectObject(dc, br)
    win32gui.Polygon(dc, [(400,20), (350,120), (450,120)] )
    
    win32gui.EndPaint(hwnd, ps)
    return 0

def OnClose(hwnd, msg, wparam, lparam):
    """Destroy window when it is closed by user"""
    win32gui.DestroyWindow(hwnd)

def OnDestroy(hwnd, msg, wparam, lparam):
    """Quit application when window is destroyed"""
    win32gui.PostQuitMessage(0)

#Define message map for window
wndproc = { win32con.WM_PAINT:OnPaint,
            win32con.WM_CLOSE:OnClose,
            win32con.WM_DESTROY:OnDestroy
            }

def CreateWindow(title,message_map,(l,t,r,b)):
    """Create a window with defined title, message map, and rectangle"""
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = 'test_win32gui_1'
    wc.style =  win32con.CS_GLOBALCLASS|win32con.CS_VREDRAW | win32con.CS_HREDRAW
    wc.hbrBackground = win32con.COLOR_WINDOW+1
    wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
    wc.lpfnWndProc=message_map
    class_atom=win32gui.RegisterClass(wc)       
    hwnd = win32gui.CreateWindow(wc.lpszClassName,
        title,
        win32con.WS_CAPTION|win32con.WS_VISIBLE|win32con.WS_SYSMENU,
        l,t,r,b, 0, 0, 0, None)
    while win32gui.PumpWaitingMessages() == 0:
        time.sleep(0.01)
    win32gui.UnregisterClass(wc.lpszClassName, None)

#Display sample window
CreateWindow('Pywin32 sample',wndproc,(100,100,500,200))