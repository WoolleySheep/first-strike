# first-strike
## Programming game between a rocket and a turret

### TODO
* Implement animation: https://stackoverflow.com/questions/9401658/how-to-animate-a-scatter-plot
* Add game timer to board
* Turret controller: Shoot if the path of the rocket and the projectile are estimated to intersect
* Rocket controller: Use all engines to "slide" towards the turret, as well as rotating
* Check game_data hasn't been tampered with between turns
* Add objects to block rocket and projectiles
### Description
The aim of the game is simple:
* The rocket has to crash into the turret
* The turret has to shoot down the rocket

One player will play as the rocket, the other as the turret.
At each timestep the players can use all of the available data
to decide what to do.
* The rocket player controls its main engine and thrusters
* The turret player controls its rotation and cannon

