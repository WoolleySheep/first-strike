# first-strike
## Programming game between a rocket and a turret

### TODO
* Buffer functions still need to be brought up to date
* Consider refactoring meta controller to be composed not inherited; how to define turret and rocket controller differently?
* Profile code properly
* Add harder game modes; limited projectiles can be fired, limited amount of engine fuel, etc.
* Reformat rocket controller
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

