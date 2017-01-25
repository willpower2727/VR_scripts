import win32gui
import re


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

	
top_windows = []
win32gui.EnumWindows(windowEnumerationHandler,top_windows)

#look for our window
for i in top_windows:
		if "Vazquez_Exp2B_V1_rev1" in i[1]:
			print i
			win32gui.ShowWindow(i[0],5)
			win32gui.SetForegroundWindow(i[0])
			break
		else:
			print('window not found')

print(top_windows)
