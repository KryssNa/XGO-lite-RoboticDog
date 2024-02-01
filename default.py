from xgolib import XGO
XGO_lite=XGO("xgolite")
for count in range(10):
	XGO_lite.action(6)
	XGO_lite.turn(100)
	time.sleep(2)
