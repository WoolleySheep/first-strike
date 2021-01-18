from animation import Animation
from helpers import Helpers
from movement import Movement
from game_parameters import process_game_parameters
from physics import Physics
from plotting import Plotting



class FirstStrike:
    def __init__(self):
        self.parameters = None
        self.history = None
        self.helpers = None
        self.physics = None
        self.movement = None
        self.plotting = None
        self.animation = None


    def play(self):

        self.parameters, self.history = process_game_parameters()
        self.helpers = Helpers(self.parameters, self.history)
        self.physics = Physics(self.parameters, self.history)
        self.movement = Movement(self.parameters, self.history, self.physics, self.helpers)
        self.plotting = Plotting(self.parameters, self.history)

        self.animation = Animation(self.parameters, self.history, self.movement, self.plotting)
        self.animation.run()


game = FirstStrike()
game.play()
