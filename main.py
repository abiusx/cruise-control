#!/usr/bin/env python

#TODO: 500ms gear shift time
import json,sys,time,math
from collections import OrderedDict
try:
	import pyglet
	pyglet_exists = True

	class Graphics(pyglet.window.Window):
		def exit(self):
			pyglet.app.exit();
		def text(self,*args,**kwargs):
			return pyglet.text.Label(*args,**kwargs)

		def __init__(self,server):
			super(self.__class__, self).__init__(width=800,height=600,resizable=True)
			self.server=server;
			self.fps_display = pyglet.clock.ClockDisplay()
			self.vertices= pyglet.graphics.vertex_list(1,"v2f")
			self.perma_batch = pyglet.graphics.Batch()
			self.temp_batch = pyglet.graphics.Batch()
			self.batch=self.temp_batch;
			self.labels=OrderedDict()
			self.legend=self.legend()
			self.pause=False
			self.time=0;
		def line(self,points,color=(255,255,255)):
			self.batch.add(len(points),pyglet.gl.GL_LINE_STRIP,None,
				("v2f",[float(all) for point in points for all in point])
				,("c3B",color*len(points))
				)
		def permanent(self):
			self.batch=self.perma_batch;
		def temporary(self):
			self.temp_batch = pyglet.graphics.Batch()
			self.batch=self.temp_batch;
		def circle(self,x,y,radius=5,color=(255,255,255,255)):
			points=[];
			for i in [math.pi/6.0 * t for t in range(0,12)]:
				points.append((math.cos(i) * radius	+x, math.sin(i) * radius+y))
	 		return self.polygon(points,color)
	 	def polygon(self,points,color=(255,255,255)):
	 		self.batch.add(len(points),pyglet.gl.GL_POLYGON,None,
				("v2f",[float(all) for point in points for all in point])
				,("c3B",color*len(points))
				)
		def update(self,dt):
			self.labels=self.server.labels();
			if (self.pause):
				return;
			# self.point(self.server.auto.x,100+1+self.server.road.path[self.server.road.block_index]*10,(255,0,0));
			self.temporary()
			y=self.server.road.path[self.server.road.block_index+1]-self.server.road.path[self.server.road.block_index]
			x=(self.server.auto.x - self.server.road.path_block_length * self.server.road.block_index)  / self.server.road.path_block_length
			y=self.server.road.path[self.server.road.block_index] + y*x
			self.circle(self.server.auto.x,100+y*10,color=(255,0,0));

			self.permanent()
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
				self.server.simulation_speed*=2;
			elif (symbol==pyglet.window.key.MINUS):
				self.server.simulation_speed/=2;
			elif (symbol==pyglet.window.key.C):
				self.server.auto.cruise_control_enabled= not self.server.auto.cruise_control_enabled
			pass;
		def on_key_press(self,symbol, modifiers):
			if (symbol==pyglet.window.key.SPACE):
				self.pause= not self.pause
			elif (symbol==pyglet.window.key.RIGHT):
				p=self.pause
				self.pause=False;
				self.update(self.dt)
				self.pause=p;

		def point(self,x,y,color=(255,255,255)):
			self.batch.add(1,pyglet.gl.GL_POINTS,None,
				("v2f",(float(x),float(y)))
				,("c3B",color)
				)
		labels={}
		def legend(self):
			return self.text("+/- 	 = Simulation Speed\nUp/Dwn = Gas\nW/S 	 = Brake\nSpace	 = Pause\nRight	 = Next Step\nC 	 = Cruise Control"
				,font_name="Courier New",anchor_x='left',anchor_y='top',x=5,y=self.height,align='left',width=250,font_size=10,multiline=True)

		def on_draw(self):
			self.clear()
			self.fps_display.draw()
			self.perma_batch.draw();
			self.temp_batch.draw();
			self.label=self.text('\n'.join(['%s: %10s' % (key ,value) if value!="-" else " " for (key,value) in self.labels.items()])
				,font_name="Courier New",anchor_x='right',anchor_y='top',x=self.width-10,y=self.height,align='right',width=250,font_size=10,multiline=True,bold=True)
			self.label.draw()
			self.legend.draw()
			return
		
		def run(self,callback,fps=60):
			self.callback=callback
			pyglet.clock.schedule_interval(self.update, 1.0/fps)
			pyglet.app.run()
except ImportError:
	pyglet_exists = False


# g=Graphics();
# g.chart([(10,2),(5,30)])
# g.point(100,100)
# g.line([(110,110),(200,200),(100,300)])
# g.line([(50,50),(300,52)])
# g.run();
# exit(0);

class JSONLoader(object):
	@classmethod
	def load(cls,file,**kwargs):
		data=open(file,"r").read()
		data=json.loads(data);
		data.update(kwargs)
		return cls(**data);
	def save(self,file):
		dict=self.__dict__
		res={}
		for key in dict:
			if not isinstance(dict[key], JSONLoader):
				res[key]=dict[key];
		open(file,"w").write(json.dumps(res,ensure_ascii=False).replace(", \"",",\n\""));



class Road(JSONLoader):
	def __init__(self,path,path_block_length,C_drag,C_rolling_resistence,C_friction,g=9.8,theta=0.0,block_index=0,**kwargs):
		kwargs=locals()
		for key, value in kwargs.items():
			setattr(self, key, value)


class Automobile(JSONLoader):
	def __init__(self,gears,differential_ratio,transmission_efficiency,wheel_radius,mass,min_rpm,max_rpm,horsepower
		,v=0.0,x=0.0,rpm=0.0,active_gear=1,gas=0.0,brake=0.0,**kwargs):
		kwargs=locals()
		self.F_traction =	\
		self.F_drag		=	\
		self.F_road		=	\
		self.F_brake 	= 	\
		self.F_slope 	= 	\
		self.F_total	= 	0.0
		for key, value in kwargs.items():
			setattr(self, key, value)
	pass;
        


class CruiseControlAutomobile(Automobile):
	def __init__(self,cruise_control_enabled=True,set_speed=40*1000/3600.0, **kwargs):
		super(self.__class__, self).__init__(**kwargs)
		self.cruise_control_enabled=cruise_control_enabled
		self.set_speed=set_speed;
		self.v=set_speed			#start off with the CC speed, or a lot of penalty will be incurred
        


class Simulator(JSONLoader):
	road=Road
	auto=Automobile
	def __init__(self,road, auto,tick_per_second,simulation_speed= 	1.0	,max_score 	=	1000.0,**kwargs):
		self.auto=auto;
		self.road=road;
		self.tick_per_second=tick_per_second;
		self.simulation_speed=simulation_speed
		self.max_score=max_score
		self.time=0.0
		self.accumulated_time=0.0
		self.ticks=0
		self.score=self.max_score
		self.finished=False

	'''
	Simple emulated automatic transmission module
	'''
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
	'''
	Ticks based on actual time
	'''
	def update(self,dt):
		self.accumulated_time+=dt;
		self.time+=dt;
		while (self.accumulated_time>1.0/self.tick_per_second/self.simulation_speed):
			self.accumulated_time-=1.0/self.tick_per_second/self.simulation_speed;
			self.tick();

	'''
	One tick of the server clock
	'''
	def tick(self):
		self.ticks+=1
		auto=self.auto
		road=self.road

		#cruise control feedback
		self.cruise_control();

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
		road.block_index 	=	(int)(math.floor(auto.x / road.path_block_length))
		if (road.block_index>=len(road.path)-1): 
			return self.end();
		road.theta		= 	math.atan(road.path[road.block_index+1] - road.path[road.block_index])

		#force calculation	
		auto.F_traction =	drive_torque / auto.wheel_radius								#motor force
		auto.F_drag		=	road.C_drag * auto.v * auto.v 									#air resistence
		auto.F_road		=	road.C_rolling_resistence * auto.v									#road resistence
		auto.F_brake 	= 	auto.brake / 100.0 * road.C_friction * road.g * auto.mass	#brake force
		auto.F_slope 	= 	math.sin(road.theta) * road.g * auto.mass
		auto.F_total	= 	auto.F_traction	- auto.F_drag - auto.F_road - auto.F_brake - auto.F_slope
		
		#speed calculation
		auto.a 			=	auto.F_total / auto.mass  
		auto.v			+=	auto.a / self.tick_per_second 
		if (auto.v<0): 
			auto.v 	=	0;			#can't go negative
		auto.x 			+= auto.v / self.tick_per_second  


		#automatic transmission
		self.automatic_transmission(throttle)

		#score calculation
		if (auto.cruise_control_enabled):
			self.score-= (auto.set_speed-auto.v)**2;
			if (self.score<0): self.score=0;
		return True;

	def cruise_control(self):
		'''
		basic stupid implementation of cruise control
		only works fine with high ticks
		'''
		auto=self.auto
		if not auto.cruise_control_enabled: return False;
		desired_speed=auto.set_speed
		if (desired_speed<auto.v):
			auto.brake+=25;
			auto.gas=0
		elif (desired_speed>auto.v):
			auto.brake=0;
			auto.gas+=25;
		else:
			auto.brake=0;
			auto.gas=5
		pass;


	def labels(self):
		auto=self.auto
		road=self.road
		labels=OrderedDict();
		labels["Score"]=format(self.score,".2f")+"";
		labels["Simulation Speed"]=format(self.simulation_speed,".1f")+"X";
		labels["Cruise Control"]=format(self.auto.set_speed*3600/1000,".1f")+" km/h" if self.auto.cruise_control_enabled else "Off";
		labels["Speed"]=format(auto.v*3600/1000.0,".1f")+" km/h" ;
		labels["Gas"]=format(auto.gas,".1f")+"%";
		labels["Brake"]=format(auto.brake,".1f")+"%";
		

		labels["1"]="-";
		labels["Real Time"]=format(self.time,".3f")+"s";
		labels["Sim Time"]=format(self.ticks / float(self.tick_per_second),".3f")+"s";
		labels["Ticks"]=str(self.ticks)
		labels["2"]="-";
		labels["RPM"]=format(auto.rpm,".0f")+"" ;
		labels["Gear"]=str(auto.active_gear)

		labels["Distance"]=format(auto.x,".2f")+" m" ;
		labels["Remaining"]=format(road.path_block_length* len(road.path)-auto.x,".2f")+" m" ;
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

		self.finished=True;
		if pyglet_exists and args.gui:
			pyglet.app.exit();
		pass
	def run(self):
		if pyglet_exists and args.gui:
			self.graphics= Graphics(self);
			path=[(x * self.road.path_block_length,y*10+100) for (x,y) in list(enumerate(self.road.path))]
			self.graphics.permanent();
			self.graphics.line(path,(0,255,0))
			self.graphics.run(self.update);
		else:
			while not self.finished:
				self.tick()
				if self.ticks%args.key_tick==0:
					print
					print "-"*30,"Tick",self.ticks,"-"*30
					print "\n".join(['%-20s: %10s' % (key ,value) if value!="-" else " " for (key,value) in self.labels().items()])
				else:
					sys.stdout.write('.')
					sys.stdout.flush()
				time.sleep(1/1000.0*args.delay)
			print "\n","-"*30,"done","-"*30


import argparse
parser = argparse.ArgumentParser(prog="CCSIM",formatter_class=argparse.RawDescriptionHelpFormatter,description='''Cruise Control Simulator

Any argument not provided will be overriden by the default simulation''')
parser.add_argument('--road', nargs=1,help='the road file',default="bumpy.road")
parser.add_argument('--car', nargs=1,help='the car file',default="CorvetteC5.car")
parser.add_argument('--sim', nargs=1,help='the simulation file',default="test.sim")
parser.add_argument('--cc', nargs=1,help='the cruise control application')
parser.add_argument('--gui',help='show simulation GUI',action='store_true',default=True)
parser.add_argument('--delay', nargs=1,type=int,help='delay between ticks in miliseconds (CLI only)',default=10)
parser.add_argument('--key-tick', nargs=1,type=int,help='which tick to show report on (CLI only)',default=100)
args = parser.parse_args()

road 		=	Road.load(args.road)
automobile 	=	CruiseControlAutomobile.load(args.car);
simulator 	=	Simulator.load(args.sim,road=road,auto=automobile);
# automobile.set_speed=automobile.v=120.0*1000/3600
simulator.run();
print "Final score:",format(simulator.score,".2f"),"/",format(simulator.max_score,".2f")," (%.2f%%)" % (simulator.score/simulator.max_score*100.0);