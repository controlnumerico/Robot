#!/usr/bin/python3
#
#  Copyright Mirco Slepko 2019
#
#  Unit: mm
#
#
#             L3
#    j2  *--------------*   j3
#        |           L4 | 
#    L2  |              *   j4
#        |           L5 |
#    j1  *              *   j5
#        |           L6 |
#    L1  |              *   j6
#                    L7 |
#                      ( )  tool
#                                   
#     

from vismach import *
import hal

## Config Vars
debug_orig_axis = True    # Enable orig (0,0,0) cross reference
debug_orig_effector = True  # Enable cross reference to end effector

toolZ_offset = 74
# Models colors
default_color = [0.5,0.5,0.5,1]
link1_color = [0.98,0.31,0,1]
link2_color = [0.98,0.31,0,1]
link3_color = [0.7,0.7,0.7,1]
link4_color = [0.98,0.31,0,1]
link5_color = [0.7,0.7,0.7,1]
link6_color = [0.98,0.31,0,1]
link7_color = [0.7,0.7,0.7,1]

tooltip_color = [0.5,0.5,0.5,1]
tip_color = [1,1,1,0]
base_color = [0.18,0.19,0.2,1]
floor_color = [1,1,1,1] 
refx_color = [0,1,0,1]
refy_color = [1,0,0,1]
refz_color = [0,0,1,1]

## HAL Pins
c = hal.component("mr6gui")
c.newpin("joint1", hal.HAL_FLOAT, hal.HAL_IN)
c.newpin("joint2", hal.HAL_FLOAT, hal.HAL_IN)
c.newpin("joint3", hal.HAL_FLOAT, hal.HAL_IN)
c.newpin("joint4", hal.HAL_FLOAT, hal.HAL_IN)
c.newpin("joint5", hal.HAL_FLOAT, hal.HAL_IN)
c.newpin("joint6", hal.HAL_FLOAT, hal.HAL_IN)
c.newpin("grip", hal.HAL_FLOAT, hal.HAL_IN)
c.ready()

## Import immobile addictional object in ambient if models file exists
exists_work_ambient = False
work_ambient = list()

def loadAmbient():

	import os
	import sys

	global work_ambient, exists_work_ambient
	
	if os.path.exists("models/ambient"):
		# Import ambient list file
		sys.path.append("models/ambient")

		def isSTL(m):
			if (".stl" in m) or (".STL" in m): return True
			else: return False
		

		try: from ambient import ambient_models
		except: print "Ambient list file not found!"

		for m in ambient_models:			
			if "show" in m:
				current = None
				if m["show"]:
					try:
						if isSTL("models/ambient/"+m["filename"]):
							current = AsciiSTL("models/ambient/"+m["filename"])
						

						if "color" in m:
							ci=m["color"]
							color = [ci[0]/255.0,ci[1]/255.0,ci[2]/255.0,ci[3]/255.0]
							current = Color(color,[current])

						if "translate" in m:
							current = Translate([current],0,0,float(m["translate"][0]))
							current = Translate([current],0,float(m["translate"][1]),0)
							current = Translate([current],float(m["translate"][2]),0,0)

						if "rotate" in m:
							current = Rotate([current],float(m["rotate"][0]),1,0,0);
							current = Rotate([current],float(m["rotate"][1]),0,1,0);
							current = Rotate([current],float(m["rotate"][2]),0,0,1);
						
						work_ambient.append(current)
					except: pass
						
		print "Found "+ str(len(work_ambient)) + " addictional ambient models"
		if len(work_ambient) > 0:
			work_ambient = Collection(work_ambient)
			exists_work_ambient = True


loadAmbient()




# end effector X-Y-Z cross reference for debug
floor = Collection([
	Box(-100,-100,-3,100,100,0),
	Color(refx_color,[CylinderX(0,5,200,2)]),
	Color(refy_color,[CylinderY(0,5,200,2)]),
	Color(refz_color,[CylinderZ(0,5,200,2)])
])


## Create Work
work = Capture()


## Create Tool
tool = Capture()

### Create Tooltip, tool with tip is attached to link7
tooltip = Capture()

# Create tip, show simple cone to indicate the position


#tip = Color(tip_color,[CylinderZ(0,3,toolZ_offset+49,0.4)])
tip = AsciiSTL(filename="models/robot/tool.stl")
tip = Translate([tip],0,0,-(toolZ_offset))


effxaxis = Color(refx_color,[CylinderX(0,0.5,50,0.5)])
effyaxis = Color(refy_color,[CylinderY(0,0.5,50,0.5)])
effzaxis = Color(refz_color,[CylinderZ(0,0.5,50,0.5)])
# Attach tooltip to tool and debug: final effector reference axis
tool = Collection([tooltip, tool, tip ,effxaxis,effyaxis,effzaxis])


tool = Rotate([tool],90,1,0,0);
tool = Translate([tool],0,-162,0)

### Create link7
link7 = AsciiSTL(filename="models/robot/link7.stl")
link7 = Color(link7_color,[link7])
link7 = Rotate([link7],90,1,0,0);
link7 = Translate([link7],0,-44,0)

# Join to tool
link7 = Collection([link7, tool])
#link7 = Translate([link7],0,0,44+44+toolZ_offset)
# Apply a dummy HAL DOF to join6
link7 = HalRotate([link7],c,"joint6",1,0,1,0)


### Create link6
link6 = AsciiSTL(filename="models/robot/link6.stl")
link6 = Color(link6_color,[link6])


 
# Join link7 to link6
link6 = Collection([link7, link6])
# Move back, joint5 rotate in origin
#link6 = Translate([link6],0,0,41)
# Apply HAL DOF to joint5
link6 = HalRotate([link6],c,"joint5",1,1,0,0)
link6 = Rotate([link6],180,0,1,0)

### Create link5
link5 = AsciiSTL(filename="models/robot/link5.stl")
link5 = Color(link5_color,[link5])
# Rotate and traslate it
link5 = Rotate([link5],90,1,0,0)
link5 = Translate([link5],0,284,0)
# Join link6 to link 5
link5 = Collection([link6, link5])
# Move back, joint4 rotate in origin
#link5 = Translate([link5],0,0,95)
# Apply HAL DOF to joint4
link5 = HalRotate([link5],c,"joint4",1,0,-1,0)


### Create link4
link4 = AsciiSTL(filename="models/robot/link4.stl")
link4 = Color(link4_color,[link4])
# Rotate and Traslate it, note 127.5 is L4 from joint4 and joint5

link4 = Translate([link4],0,386.3,0)
link4 = Translate([link4],0,0,-84)
# Join link5 to link4
link4 = Collection([link5, link4])
# Move back, joint3 rotate in origin
link4 = Translate([link4],0,-386.3,0)
link4 = Translate([link4],0,0,84)
link4 = Rotate([link4],  -180,0,0,1)
# Rotate it , load model with elbow to negative Z position
#link4 = Rotate([link4],72,1,0,0)
# Apply HAL DOF to joint3
link4 = HalRotate([link4],c,"joint3",1,1,0,0)




### Create link3 (spalle lunghe)
link3 = AsciiSTL(filename="models/robot/link3.stl")
link3 = Color(link3_color,[link3])
# Rotate and Traslate it, note 81 is L2 from joint2 and joint3
link3 = Rotate([link3],  90,0,1,0)



link3 = Translate([link3],0,0,-312)

link3 = Collection([link4, link3])
link3 = Rotate([link3],  180,0,0,1)

link3 = Translate([link3],0,0,312)

# Apply HAL DOF to joint2
link3 = Rotate([link3],-180,0,1,0)
# Rotate it , load model with "" to negative Z position
link3 = HalRotate([link3],c,"joint2",1,1,0,0)
link3 = Rotate([link3],90,1,0,0)




### Create link2
link2 = AsciiSTL(filename="models/robot/link2.stl")
link2 = Color(link2_color,[link2])
# Rotate and Traslate it, note 120 is L1 from joint1 and joint2
link2 = Rotate([link2], -180,0,0,1)

link2 = Translate([link2],0,0,-260)
link2 = Translate([link2],0,81,0)

link2 = Collection([link3, link2]) 

link2 = Translate([link2],0,0,260)
link2 = Translate([link2],0,-81,0)


# Apply HAL DOF to joint1
link2 = HalRotate([link2],c,"joint1",1,0,0,1)
# Traslate it, return to origin, link2 rotate around origin
link2 = Translate([link2],0,0,120)
link2 = Rotate([link2], -90,0,0,1)



### Create link1, base
link1 = AsciiSTL(filename="models/robot/link1.stl");
link1 = Color(link1_color,[link1])
link1 = Rotate([link1], 0,0,0,1)

### MR-6 object, assembly link1 to link2
mr6 = Collection([link2, link1])

if exists_work_ambient:
	model = Collection([tooltip, mr6, floor, work, work_ambient])
else:
	model = Collection([tooltip, mr6, floor, work])

### Main Scene
main(model, tooltip, work,1270,1270,None,-75,600)

