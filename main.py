#!/bin/env python
import pyglet
import sys
import time
import math
def chart(data):
	vertices=[x for item in data for x in item];
	# print vertices
	window = pyglet.window.Window()

	label = pyglet.text.Label('Speed Chart',
	                          font_name='Times New Roman',
	                          font_size=24,
	                          x=window.width//20, y=window.height-20,
	                          anchor_x='left', anchor_y='top')


	vertex_list = pyglet.graphics.vertex_list(len(data),
	    ('v2i', vertices),
	    # ('c3B', (0, 0, 255, 0, 255, 0))
	)
	@window.event
	def on_draw():
		window.clear()
		label.draw()
		vertex_list.draw(pyglet.gl.GL_POINTS)
	pyglet.app.run()



# chart([(10,2),(5,3)])
# exit(0);



#world definition
C_drag	=	0.4257	# resistence constant 
C_road_rolling 	=	12.8	# rolling resistence constant 
C_road_friction	=	0.7 	# braking resistence
time_length 	=	1000 	# seconds
g 				= 	9.8	 	# gravity

# car definition
gear_ratio = [0,2.66,1.78,1.30,1.0,.74,.50] #Corvette C5 hardtop
differential_ratio = 3.42
transmission_efficiency =.7
wheel_radius = 0.34 # meters
mass	=	1500.0 #kg
min_rpm = 	1000
max_rpm =	6000
horsepower	=	280.0

v 		= 	120 * 1000 / 3600.0 # 20 km/h
rpm		=	0.0;
active_gear	=	1;

#dynamic parameters
gas		=	00.0
brake 	=	100.0
x=0
tick_per_second = 10
data= [];

#TODO: fix brake. the torque is not valid

def automatic_transmission(active_gear,v,rpm,max_rpm,throttle):
	if (rpm/max_rpm + throttle > 1.0):
		return active_gear+1;
	elif (rpm/max_rpm + throttle < .3):
		return active_gear-1;
	else:
		return active_gear;
for tick in xrange(1,tick_per_second*time_length):
	#validation
	if (gas > 100): gas = 100;
	if (gas< 0): 	gas = 0;
	if (brake<0):	brake =0;
	if (brake>100):	brake=100;

	#engine rpm calculation
	throttle	= 	gas / 100.0
	wheel_rotation_rate	=	v/wheel_radius;
	rpm 	= 	wheel_rotation_rate * gear_ratio[active_gear] * differential_ratio * 60 /2.0 / math.pi
	if( rpm < min_rpm ):
		rpm 	= 	min_rpm;   	
	elif (rpm> max_rpm):
		rpm 	= 	max_rpm;
	
	#torque calculation
   	max_torque 	= 	7119.0 * horsepower  / rpm; 
	engine_torque 	= 	throttle  * max_torque
	## brake_torque	=	brake/100.0 * C_road_friction  * g
	drive_torque 	= 	engine_torque * gear_ratio[active_gear] * differential_ratio * transmission_efficiency

	#force calculation
	F_traction 	=	drive_torque / wheel_radius
	F_drag		=	C_drag * v *v 	#air resistence
	F_road		=	C_road_rolling * v		#road resistence
	## F_brake 	= 	brake_torque
	F_total		= 	F_traction	- F_drag - F_road ##- F_brake

	#speed calculation
	a 			=	F_total / mass  - (brake/100.0 * g /2.0)
	v			+=	a / tick_per_second 
	if (v<0): v=0; #can't go negative
	x 			+= v / tick_per_second


	#automatic transmission
	active_gear = automatic_transmission(active_gear,v,rpm,max_rpm,throttle)
	if (active_gear>=len(gear_ratio)): active_gear=len(gear_ratio)-1;
	if (active_gear<1): active_gear=1;

	if (v==0): break;
	data.append((int(tick/tick_per_second),int(v*10)));
	sys.stdout.flush()
	# time.sleep(.001)
	print tick,") V:",format(v,".2f")\
		,"Gear:",active_gear,"RPM:",rpm,"X=",x;

chart(data);