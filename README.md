# first-strike
## Programming game between a rocket and a turret

### TODO
* Turret controller: Rotate towards the angle required for a leading shot
* Rocket controller: Use all engines to "slide" towards the turret, as well as rotating, account for current movement
* Convert modules into proper classes
* Check game_data hasn't been tampered with between turns
* Add objects to block rocket and projectiles
* Test for controller execution time
* Add turret reload graph (increase red to full, then green when ready)
* Add rocket g forces
* Fix "projectiles not disappearing when off board" problem 
* Check game settings for validity before beginning the game
* Exercise controllers for fitness; provide them with situations and validate responses
### Description
The aim of the game is simple:
* The rocket has to crash into the turret
* The turret has to shoot down the rocket

One player will play as the rocket, the other as the turret.
At each timestep the players can use all of the available data
to decide what to do.
* The rocket player controls its main engine and thrusters
* The turret player controls its rotation and cannon

