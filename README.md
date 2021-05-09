# first-strike
## Programming game between a rocket and a turret
### Description
The aim of the game is simple:
* The rocket has to crash into the turret
* The turret has to shoot down the rocket

One player will provide the algorithm that controls the rocket, the other play the algorithm for the turret.  May the best algorithm win!
### Running a game
1. Install the module requirements using ``pip install -r requirements.txt``.  This only has to be done once.
3. Executing the following command: ``python first_strike/game.py``
4. Wait for the game window to appear
### Player vs default controllers
It is possible to play first strike against either another person's controller, or against the default controller than comes with the game.  
This is set in ``game_parameters.json`` with the parameters ``rocket_active_controller`` and ``turret_active_controller``.  Setting these to "default" uses the inbuilt controller (aka: the code in ``default_controllers``), while setting it to "player" uses a player-defined controller (``player_controllers``).
### Terminology
* **Controller**: When you hear 'controller' think 'algorithm that controls a player object'.  If there is a need to be specific, they will be referred to as the 'rocket controller' and 'turret controller' respectively.
### How the game works
The game is divided into discrete timesteps (eg: 10ms).
Every timestep, all of the available game data is made available to the controllers.  This includes:
* The current and past positions of all game objects (rocket, turret, projectiles, obstacles)
* Game object metadata (eg: the radius of each obstacle, how fast a projectile is, etc)
* Player-controlled object actions (eg: when the turret last fired, current rocket main engine force, etc)
Using this information, each player's algorithm should calculate what actions to take in the next timestep.
The rocket can control:
  * The force produced by its main (rear) engine
  * The force produced by each of its 4 thrusters (left-front, left-rear, right-front, right-rear)
The turret can control:
  * The speed of its rotation
  * Whether it should fire a projectile
These commands are then processed and, if valid, executed as the game advances by 1 timestep.
The cycle then repeats; all of the game data is made available and the controllers calculate their next moves.  This continues until a win condition is reached.
### Ways to win
As specified in the description, the main 'win' conditions are as follows:
* The rocket crashes into the turret (rocket win)
* The turret shoots down the rocket (turret win)
The turret has several additional win conditions, which mostly rely on the rocket making a mistake:
* Rocket flies outside the game board
* Rocket crashes into an obstacle
The game can also be lost through algorithm malfunction.  If any of these occur, the other player wins:
* Invalid commands are produced by a controller
* Unhandled exception is raised
* Allowed computation time is exceeded
* Game variables and parameters are tampered with
Additionally, there are several outcomes that count as a draw:
* Game timer expires
* Rocket win condition and turret win condition are satisfied in the same turn
### Code structure
#### A note on OOP
This game uses basic OOP concepts, so it would be advisable to have a working knowledge of these before beginning.  Specifically the concepts of classes, methods and attributes should be understood.
Furthermore the documentation in the README is designed to be brief and to the point, providing the bare minimum information needed to start playing.  Classes listed here may have additional attributes or methods.  It is strongly advised to refer to the codebase directly; docstrings, typehints and comments provide excellent insight on how things are to be used.
#### Where to put your code
The codebase of first-strike is not overly large, but players need only concern themselves with a small fraction of it: the files within ``player_controllers``.  Inside this directory are two files:
* ``rocket_controller.py``
* ``turret_controller.py``
``rocket_controller.py`` is edited by the player programming the rocket controller, and vice-versa for the turret.
Each file contains a single class, ``<Rocket/Turret>Controller``, with a basic init and a single method ``calc_inputs``.  The game variables can be read from the attributes of this class, while the the output of ``calc_inputs`` will be treated as commands from the controller.  You are welcome to add your own methods to ``<Rocket/Turret>Controller``, as well as to create new classes.  However try to keep all of your code within a single file.
##### Return from calc_inputs method
The exact format of the return from ``calc_inputs`` depends on whether it is the rocket or turret controller.  If any of the restrictions are broken, then the offending controller will immediately lose.
###### Rocket commands
Type: List[float, float, float, float]
Contents: [main_engine_force, left_front_thruster_force, left_rear_thruster_force, right_front_thruster_force, right_rear_thruster_force]
Units: [N, N, N, N, N]
Eg: [100.0, 90.0, 90.0, 0.0, ]
Restrictions:
* No force can be less than 0.
* The engine force cannot be greater than the maximum engine force, and no thruster force can be greater than the maximum thruster force.
###### Turret commands
Type: List[float, bool]
Contents: [turret_rotation_velocity, fire_projectile]
Units: [rad/s, NA]
Eg: [0.7, True]
Restrictions:
* The absolute value of the turret rotational velocity cannot be greater than the maximum turret rotation velocity.
* The turret cannot be fired if the minimum firing interval time has not elapsed.  If no projectile has been fired since the game commenced, then the turret can always fire.
#### controller attributes
Both classes inherit from ``Controller``, a class which can be found ``controller.py``.  Both classes have the following attributes, which are themselves classes:
* parameters: Data
* history: Data
* physics: Tools
* helpers: Tools
* controller_helpers: Tools
##### Data
The 'data' that is available to each controller to make its decisions.  Data is split into two classes:
* Parameters
* History
##### Parameters (parameters.py)
Parameters are constants that remain fixed for the duration of the game.  There are 4 attributes, each a class:
* Environment
* Time
* Rocket
* Turret
###### Environment (parameters.py)
Parameters relating to features of the game board.
* width (m): Width of the game board.
* height (m): Height of the game board.
* obstacles (list): All of the obstacles on the board.  Each obstacle has two parameters:
  * location (m): The location of the obstacle as an (x, y) coordinate
  * radius (m): The radius of the obstacle.
###### Time (parameters.py)
Parameters relating to time within the game.
* timestep (s): Duration of the timestep between each game turn.
* max_game_time (s): If game time exceeds this value, it will be declared a draw.
###### Rocket (parameters.py)
Parameters relating to the rocket.
* mass (kg): Mass of the rocket
* length (m): Length of the rocket (nose-to-tail)
* max_main_engine_force (N): Maximum thrust the main engine can generate.
* max_thruster_force: Maximum thrust each of the thrusters can generate.
* engine_labels: Names of each of the engines.
* target_radius (m): Effective radius of the rocket for determining collisions.
* moment_of_inertia (kg*m^2): Moment of inertia of the rocket around the center of mass.
* abs_thruster_moment_arm (N*m): Absolute moment arm of all thrusters.
* thruster_labels: The names of each of the thrusters.
###### Turret (parameters.py)
Parameters relating to the turret.
* radius (m): Effective radius of the rocket
* location (m): The location of the obstacle as an (x, y) coordinate
* max_rotation_speed (rad/s): Maximum speed that the turret can rotate.
* projectile_speed (m/s): The speed all projectiles travel at.
* min_firing_interval (s): The minimum allowed time interval between the turret firing.
##### History (history.py)
History captures the past (and current) state of the game.
It is divided into:
* Rocket
* Turret
* Projectiles (list)
* Time
Note that many of the history variables take the form of lists, with the most recent element in the list corresponding to the most recent value.  So the last element of rocket.locations would correspond to the current rocket location, while the 2nd last element would correspond to its position 1 timestep ago.
Note also that the attribute names are plural (location**s**, angle**s**, etc).  This is because the attributes are lists, with multiple entries.  If you wish to get the most recent value of a list, you can either select the index normally, or you can use the singular version of the attribute name (location, angle, etc).  This will return the last value in the list.  Note that if there are currently no values in the list, then an IndexError exception will be raised.
###### Rocket (history.py)
The past and present state of the rocket.
* locations (m): The location of the COM of the rocket as an (x, y) coordinate
* angles (rad): The angle of the rocket relative to the x axis
* main_engine_forces (N): The force produced by the main rear engine
* left_front_thruster_forces (N): The force produced by the left-front thruster.
* left_rear_thruster_forces (N): The force produced by the left-rear thruster.
* right_front_thruster_forces (N): The force produced by the right-front thruster.
* right_rear_thruster_forces (N): The force produced by the right-rear thruster.
###### Turret (history.py)
The past and present state of the turret.
* angles (rad): The angle of the turret barrel relative to the x axis.
* rotation_velocities (m/s): The speed and direction of the turret rotation.
* when_fired (s): The times when the turret has fired a projectile.
###### Projectiles (history.py)
The past and present state of all projectiles fired by the turret.
* firing_angle (rad): The angle of the turret barrel when the projectile was fired
* launch_time (s): The time when the projectile was fired by the turret.
* on board: Whether the projectile is currently on the board.  A projectile is removed from the board when it either:
  * Moves outside the board boundaries
  * Hits an obstacle
#### Tools
Tools are pre-created classes with methods that may be useful in the creation of a controller.  There are 3 tool classes provided:
* physics
* helpers
* controller helpers
##### Physics (physics.py)
Methods for calculating the linear/angular velocity/acceleration of the rocket based on recent locations.
##### Helpers (helpers.py)
Methods for checking if an action is valid; for example, is the turret able to fire, or is an object within the board limits.  Mainly used by the internal game logic but can be useful to players.
Location: helpers
##### Controller helpers (controller_helpers.py)
Miscellaneous methods: will a projectile fired now hit the rocket, what is the angle between rocket and turret, etc.  Useful in contructing both rocket and turret controllers.
### Maths helpers (maths_helpers.py)
This module does not depend upon any other game parameters; as such, it is treated differently to the  This module contains functions, classes and methods of a mathematical bent that are used within the game logic.  It also contains the ``Coordinate`` class which is used for defining (x, y) points in this game. 
### Changing game variables
All of the game's parameters are controlled by ``game_parameters.json``.  All of these parameters can be modified, though before the game can begin they will be validated by the checks in ``game_parameters.py``.
Parameters in this file can be broadly seperated into:
* Gameplay parameters
* Development parameters
* Visual parameters
#### Gameplay parameters
These affect how objects interact on the board. You can do such things as:
* Specify the number, locations and sizes of obstacles (to have no obstacles, set obstacles = None or [])
* Change the speed of projectiles
* Set the starting location of the rocket
#### Developer parameters
useful when developing your controller; certain game settings can be suspended or modified.
* Play against another person's controller, or use the inbuilt default controller.
llowing you to play against a default controller
* Raise and print error traces for easier development.
* Don't track execution time.
#### Visual parameters
Change the look of the game board and the objects on it.  These have no effect on gameplay.
# Miscellaneous
* All angles are measured in radians, in the range -pi < theta <= pi
* Games that go for longer than 40s tend to slow down signficantly due to lists getting quite large.



### MJW TODO (not player related)
* Add typing and docstrings, especially to the user facing stuff
* Reformat docstrings using modified NumpyDoc format
* Convert type to isinstance
* Write "how to play"
* Review controller helpers and see what can go
* Consider refactoring meta controller to be composed not inherited; how to define turret and rocket controller differently?
* Profile code properly
* Add harder game modes; limited projectiles can be fired, limited amount of engine fuel, etc.
* Add a max to turret attraction strength, just like there's a min.
* Write a proper test suite.
* Reformat rocket controller
* Random board generator
* Fix error where rocket is directly behind the turret and flying towards it
* Add explosion animations
* Only avoid front arc of fire; find a way to ignore the line behind the barrel
* Re-add controller complexity: rocket hit turret first, projectile hits obstacle first, etc
* Make RelativeObjects methods more atomic - only return the time.
    * Locations and distances can be calculated seperately
* Rocket is attracted to areas where the turret's line of fire is blocked by obstacles
* More difficult game mode; turret can't see rocket when it is obscured by an obstacle
* Cache repeated calls, clear at end of each turn
* Consolidate projectile launch times into a single varable.  Currently tracked in two places
