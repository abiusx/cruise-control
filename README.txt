== Requirements ==
You need python to run the application.

If you don't have python, download Python 2.7 from Python.org
If you're installing on Windows, make sure in the installation process you select "Add Python.exe to PATH", otherwise you have to do that yourself.

You need "pyglet" (an OpenGL wrapping for Python) to run the GUI. If you have python installed, you can get it with:

$ easy_install pyglet

If you don't want to run in GUI, you don't need pyglet.


== Running ==
Use terminal, change directory to the application folder, and then:

$ python main.py 

To run, and:

$ python main.py -h

To see all available options.


== Support ==
E-mail cc1@abiusx.com for any questions.


== Technical Details ==
The simulation formula and details can be seen in Simulator::tick function inside main.py. A crude cruise control is already implemented in the system for you to see.

The simulator options can be seen with -h as argument in command line.

Your cruise control app should process the request as fast as possible, there's only a fraction of a second time for the IPC (inter-process communication) to happen. This time can be modified using the --delay option (default is 20 miliseconds). This can be modified in GUI mode using the simulation speed, to get 25 miliseconds you need to have ticks_per_second * simulation_speed be less than 40, otherwise the cruise control app will lag behind.

Your system might be slower on IPC, try using a higher --delay value (up to 200) to see if you get better scores.