#!/bin/env python

#TODO: 500ms gear shift time
import pyglet
import sys
import time
import math
from collections import OrderedDict
class Graphics(pyglet.window.Window):
	def exit(self):
		pyglet.app.exit();
	def text(self,*args,**kwargs):
		return pyglet.text.Label(*args,**kwargs)

	def __init__(self,server):
		super(self.__class__, self).__init__(width=800,resizable=True)
		self.server=server;
		self.fps_display = pyglet.clock.ClockDisplay()
		self.vertices= pyglet.graphics.vertex_list(1,"v2f")
		self.batch = pyglet.graphics.Batch()
		self.labels=OrderedDict()
		self.pause=False
		self.time=0;
	def line(self,points,color=(255,255,255)):
		
		self.batch.add(len(points),pyglet.gl.GL_LINE_STRIP,None,
			("v2f",[float(all) for point in points for all in point])
			,("c3B",color*len(points))
			)
	def update(self,dt):
		self.labels=self.server.labels();
		if (self.pause):
			return;
		self.point(self.server.auto.x,100+1+self.server.road.path[self.server.road.position]*10,(255,0,0));
		self.point(self.server.auto.x,self.server.auto.v,(255,255,0))

		self.dt=dt;
		self.callback(dt);

	def on_key_release(self,symbol, modifiers):
		if (symbol==pyglet.window.key.ESCAPE):
			pyglet.app.exit()
		elif (symbol==pyglet.window.key.UP):
			self.server.auto.gas+=5;
		elif (symbol==pyglet.window.key.DOWN):
			self.server.auto.gas-=5;
		elif (symbol==pyglet.window.key.W):
			self.server.auto.brake+=5;
		elif (symbol==pyglet.window.key.S):
			self.server.auto.brake-=5;
		elif (symbol==pyglet.window.key.EQUAL):
			self.server.speed*=2;
		elif (symbol==pyglet.window.key.MINUS):
			self.server.speed/=2;
		pass;
	def on_key_press(self,symbol, modifiers):
		if (symbol==pyglet.window.key.SPACE):
			self.pause= not self.pause
		elif (symbol==pyglet.window.key.RIGHT):
			self.callback(self.dt)

	def point(self,x,y,color=(255,255,255)):
		self.batch.add(1,pyglet.gl.GL_POINTS,None,
			("v2f",(float(x),float(y)))
			,("c3B",color)
			)
	labels={}
	def on_draw(self):
		self.clear()
		self.fps_display.draw()
		self.batch.draw();
		self.label=self.text('\n'.join(['%s: %9s' % (key ,value) if value!="-" else " " for (key,value) in self.labels.items()])
			,font_name="Courier",anchor_x='right',anchor_y='top',x=self.width-10,y=self.height,align='right',width=250,font_size=10,multiline=True,bold=True)
		self.label.draw()
		return
	
	def run(self,callback,fps=60):
		self.callback=callback
		pyglet.clock.schedule_interval(self.update, 1.0/fps)
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
road.theta				=	0 		# road initial angle
road.position 			=	0
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

automobile.F_traction =	\
automobile.F_drag	=	\
automobile.F_road	=	\
automobile.F_brake 	= 	\
automobile.F_slope 	= 	\
automobile.F_total	= 	0.0


class Server(object):
	road=Road
	auto=Automobile
	def __init__(self,road, auto):
		self.auto=auto;
		self.road=road;
		self.time=0.0
		self.t=0.0
		self.ticks=0

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
	def update(self,dt):
		self.t+=dt;
		self.time+=dt;
		while (self.t>1.0/self.tick_per_second):
			self.t-=1.0/self.tick_per_second;
			self.tick();

	def tick(self):
		self.ticks+=1
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
		road.position 	=	(int)(math.floor(auto.x / road.path_block_length))
		if (road.position>=len(road.path)-1): 
			return self.end();
		road.theta		= 	math.atan(road.path[road.position+1] - road.path[road.position])

		#force calculation	
		auto.F_traction =	drive_torque / auto.wheel_radius								#motor force
		auto.F_drag		=	road.C_drag * auto.v * auto.v 									#air resistence
		auto.F_road		=	road.C_road_rolling * auto.v									#road resistence
		auto.F_brake 	= 	auto.brake / 100.0 * road.C_road_friction * road.g * auto.mass	#brake force
		auto.F_slope 	= 	math.sin(road.theta) * road.g * auto.mass
		auto.F_total	= 	auto.F_traction	- auto.F_drag - auto.F_road - auto.F_brake - auto.F_slope
		
		#speed calculation
		auto.a 			=	auto.F_total / auto.mass  
		auto.v			+=	auto.a / self.tick_per_second * self.speed
		if (auto.v<0): 
			auto.v 	=	0;			#can't go negative
		auto.x 			+= auto.v / self.tick_per_second  * self.speed


		#automatic transmission
		self.automatic_transmission(throttle)
		return True;


	def labels(self):
		auto=self.auto
		road=self.road
		labels=OrderedDict();
		labels["Simulation Speed"]=format(self.speed,".1f")+"X";
		labels["Time"]=format(self.time,".3f")+"s";
		labels["Ticks"]=str(self.ticks)
		labels["1"]="-";
		labels["Gas"]=format(auto.gas,".1f")+"%";
		labels["Brake"]=format(auto.brake,".1f")+"%";
		labels["Speed"]=format(auto.v*3600/1000.0,".1f")+" km/h" ;
		labels["2"]="-";
		labels["RPM"]=format(auto.rpm,".0f")+"" ;
		labels["Gear"]=str(auto.active_gear)
		# g.labels["v"]=format(auto.v,".1f")+" m/s" ;
		labels["Distance"]=format(auto.x,".2f")+" m" ;
		labels["3"]="-";
		labels["Slope"]=format(road.theta*180/math.pi,"2.1f")+"" ;
		labels["Drive Force"]=format(auto.F_traction,"0.0f")+" N" ;
		labels["Air Resistence"]=format(auto.F_drag,"0.0f")+" N" ;
		labels["Road Resistence"]=format(auto.F_road,"0.0f")+" N" ;
		labels["Brake Resistence"]=format(auto.F_brake,"0.0f")+" N" ;
		labels["Slope Force"]=format(auto.F_slope,"0.0f")+" N" ;
		labels["Total Force"]=format(auto.F_total,"0.1f")+" N" ;
		
		return labels;

		
	def end(self):
		pass
	def run(self):
		self.graphics= Graphics(self);
		path=[(x * self.road.path_block_length,y*10+100) for (x,y) in list(enumerate(self.road.path))]
		self.graphics.line(path,(0,255,0))
		# self.graphics.line([(0,100),(self.graphics.width,100)],(255,255,255))
		self.graphics.run(self.update);

		

server = Server(road,automobile);
print "Track length:",road.path_block_length* len(road.path)
server.tick_per_second 	= 	100 		# how many ticks should constitute one second of simulation time
server.data= [];
server.speed = 4.0;						# speed / tick_per_second gives simulation step time
server.run();
