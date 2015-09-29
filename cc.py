import sys
on = False;
desired_speed=0
while True:
	s = raw_input(	)
	if s[0:8]=="Command ":
		command=s[8:]
		print "Command received: ",command
		if command=="OFF":
			on = False
		elif command=="SET":
			if on is False:
				desired_speed=float(params["Speed"])
				on = True
			else:
				desired_speed-=1.0/3600.0*1000
		elif command=="RES":
			if on is False:
				on = True
			else:
				desired_speed+=1.0/3600.0*1000
	else:
		params=dict(param.split(" ") for param in s.split(";"))
		if on:
			current_speed=float(params["Speed"]);
			gas=float(params["Gas"]);
			brake=float(params["Brake"]);
			if current_speed<desired_speed:
				if brake!=0:
					brake=0
					print "Brake: ",brake
				gas+=25
				print "Gas: ",gas
			elif current_speed>desired_speed:
				brake+=25
				print "Brake: ",brake
				if gas!=0:
					gas=0
					print "Gas: ",gas

	sys.stdout.flush()