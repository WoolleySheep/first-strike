# first-strike
## Programming game between a rocket and a turret

### TODO
* Add typing and docstrings, especially to the user facing stuff
* Reformat docstrings using modified NumpyDoc format
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
### Description
The aim of the game is simple:
* The rocket has to crash into the turret
* The turret has to shoot down the rocket

One player will play as the rocket, the other as the turret.
At each timestep (or 'turn') the players can use all of the available data
to decide what to do.
* The rocket player controls its main engine and thrusters
* The turret player controls its rotation and cannon

### Ways to win
Other ways for the rocket to lose:
* Fly outside the game board
* Crash into an obstacle
Ways to draw:
* Game timer expires
* Rocket win condition and turret win condition are satisfied in the same turn

