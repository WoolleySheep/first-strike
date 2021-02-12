# first-strike
## Programming game between a rocket and a turret

### TODO
* Don't dodge projectiles if you would be within the radius of the turret or an obstacle
* Reformat rocket controller
* Allow for exception catching and default/player controller use to be set seperately for rocket and turret
* Move engine names from animation to rocket parameters
* Move a lot of hardcoded parameters to the parameters json
* Fix "projectiles not disappearing when off board" problem
* Random board generator
* Add typing and docstrings
* Write "how to play"
### Description
The aim of the game is simple:
* The rocket has to crash into the turret
* The turret has to shoot down the rocket

One player will play as the rocket, the other as the turret.
At each timestep the players can use all of the available data
to decide what to do.
* The rocket player controls its main engine and thrusters
* The turret player controls its rotation and cannon

