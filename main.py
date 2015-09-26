#!/bin/env python
import pyglet
import sys
import time
import math
class Graphics(pyglet.window.Window):
	def __init__(self):
		super(self.__class__, self).__init__(width=800,resizable=True)
		self.label = pyglet.text.Label('Speed Chart',
		                          font_name='Times New Roman',
		                          font_size=24,
		                          x=self.width//20, y=self.height-20,
		                          anchor_x='left', anchor_y='top')

	_points=[]
	_lines=[]
	def line(self,points,color=(255,255,255)):
		self._lines.append({"color":color,"points":[float(all) for point in points for all in point]})
		pass;

	def chart(self,points):
		self._points.extend([float(x) for item in points for x in item]);

	def point(self,x,y):
		self._points.extend([float(x),float(y)]);

	def on_draw(self):
		self.clear()
		self.label.draw()
		if (self._points):
			vertices= pyglet.graphics.vertex_list(len(self._points)/2,
			    ('v2f', self._points),
			    # ('c3B', (0, 0, 255, 0, 255, 0))
			)
			vertices.draw(pyglet.gl.GL_POINTS)
		if (self._lines):
			for line in self._lines:
				points=line["points"];
				color=line["color"];
				if (type(points[0])==int):
					t="i"
				elif (type(points[0])==float):
					t="f";
				else:
					raise TypeError("invalid type sent to line")


				pyglet.gl.glColor3f(*[x/255.0 for x in color]);
				vertices= pyglet.graphics.vertex_list(len(points)/2,('v2f', points))
				vertices.draw(pyglet.gl.GL_LINE_STRIP)
	
	def show(self):
		pyglet.app.run()


# g=Graphics();
# g.chart([(10,2),(5,30)])
# g.point(100,100)
# g.line([(110,110),(200,200),(100,300)])
# g.line([(50,50),(300,52)])
# g.run();
# exit(0);






class Road(object):
	pass;
road = Road();
road.C_drag	=	0.4257	# resistence constant 
road.C_road_rolling 	=	12.8	# rolling resistence constant 
road.C_road_friction	=	0.7 	# braking resistence (dry asphalt)
road.g 					= 	9.8	 	# gravity
road.path 				= 	[4,4,4,4.5,5,5.5,6,6.7,6.8,6.9,7,7.5,8,8,8,8,8,8,8,8,8,8,8,8,8,8,7.5,7,6,5,4,3,2,
							1.5,1,1,1,1,2,3,3,2,2,2,3,3,2,2,2.5,2.5,2.6,2.7,2.8,3,3.5,4,4.5,5,4.5,4.5,4.5,4]
road.path.extend([4] * 20)					
road.path_block_length	=	10
class Automobile(object):
	pass;

automobile= Automobile();
automobile.gears=[0,2.66,1.78,1.30,1.0,.74,.50] 	#Corvette C5 hardtop
automobile.differential_ratio = 3.42
automobile.transmission_efficiency =.7
automobile.wheel_radius = 0.34 							# meters
automobile.mass	=	1500.0 								# kg
automobile.min_rpm = 	1000.0
automobile.max_rpm =	6000.0
automobile.horsepower	=	280.0

automobile.v 			= 	20 * 1000 / 3600.0 			# speed 20 km/h
automobile.x 			=	0
automobile.rpm			=	0.0;
automobile.active_gear	=	1;
automobile.gas			=	50.0
automobile.brake 		=	0.0

class Server(object):
	road=Road
	auto=Automobile
	def __init__(self,road, auto):
		self.auto=auto;
		self.road=road;
	def automatic_transmission(self,throttle):
		auto=self.auto
		#let rpm go higher with higher throttle
		if ( auto.rpm/auto.max_rpm>max(min(throttle,5250/auto.max_rpm),.6)):
		# if ( rpm/max_rpm>.7):
			auto.active_gear+=1;
		elif (auto.rpm/auto.max_rpm  < 0.25 + auto.min_rpm/auto.max_rpm):
			auto.active_gear-=1;
		if (auto.active_gear>=len(auto.gears)): auto.active_gear=len(auto.gears)-1;
		if (auto.active_gear<1): auto.active_gear=1;

	def tick(self,tick):
		auto=self.auto
		road=self.road
		#validation
		if (auto.gas > 100): 	auto.gas = 100;
		if (auto.gas< 0): 		auto.gas = 0;
		if (auto.brake<0):		auto.brake =0;
		if (auto.brake>100):	auto.brake=100;

		#engine rpm calculation
		throttle	= 	auto.gas / 100.0
		wheel_rotation_rate	=	auto.v/auto.wheel_radius;
		auto.rpm 	= 	wheel_rotation_rate * auto.gears[auto.active_gear] * auto.differential_ratio * 60 /2.0 / math.pi
		if( auto.rpm < auto.min_rpm ):
			auto.rpm 	= 	auto.min_rpm;   	
		elif (auto.rpm> auto.max_rpm):
			auto.rpm 	= 	auto.max_rpm;
		
		#torque calculation
	   	max_torque 	= 	7119.0 * auto.horsepower  / auto.rpm; 
		engine_torque 	= 	throttle  * max_torque
		drive_torque 	= 	engine_torque * auto.gears[auto.active_gear] * auto.differential_ratio * auto.transmission_efficiency

		#slope calculation
		position 	=	(int)(math.floor(auto.x / road.path_block_length))
		if (position>=len(road.path)-1): 
			return False;
		theta		= 	math.atan(road.path[position+1] - road.path[position])

		#force calculation	
		F_traction 	=	drive_torque / auto.wheel_radius								#motor force
		F_drag		=	road.C_drag * auto.v * auto.v 									#air resistence
		F_road		=	road.C_road_rolling * auto.v									#road resistence
		F_brake 	= 	auto.brake / 100.0 * road.C_road_friction * road.g * auto.mass	#brake force
		F_slope 	= 	math.sin(theta) * road.g * auto.mass
		F_total		= 	F_traction	- F_drag - F_road - F_brake - F_slope
		## print road.path[position+1] - road.path[position],format(theta*180/math.pi,".1f"),F_slope;
		
		#speed calculation
		auto.a 			=	F_total / auto.mass  
		auto.v			+=	auto.a / self.tick_per_second
		if (auto.v<0): 
			auto.v 	=	0;			#can't go negative
		auto.x 			+= auto.v / self.tick_per_second


		#automatic transmission

		if (auto.v<.005): return False; ##stopped
		self.data.append((int(auto.x),int(auto.v)));
		sys.stdout.flush()
		# time.sleep(.001)
		print tick,")t=",tick/self.tick_per_second,"V=",format(auto.v/1000.0*3600,".1f")\
			,"Gear:",auto.active_gear,"RPM:",format(auto.rpm,".0f"),"X=",format(auto.x,".1f");
		
		self.automatic_transmission(throttle)
		
		return True;
	def run(self):
		for tick_index in xrange(1,self.tick_per_second*self.time_length):
			if (self.tick(tick_index) is False): break;
		g= Graphics();
		g.chart((x*1,y*2+100) for (x,y) in self.data);
		path=[(x * self.road.path_block_length,y*10) for (x,y) in list(enumerate(self.road.path))]
		g.line(path,(127,127,0));
		g.show()

server = Server(road,automobile);
print "Track length:",road.path_block_length* len(road.path)
server.tick_per_second 	= 	5
server.time_length 		=	30 		# seconds
server.data= [];
server.run();
print automobile.v*3600/1000