from animation import Animation
from determine_winner import DetermineWinner
from meta_controller import Controllers
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
        self.controllers = None
        self.animation = None

    def play(self):

        controller_parameters, self.visual, self.parameters, self.history = process_game_parameters()
        self.helpers = Helpers(self.parameters, self.history)
        self.physics = Physics(self.parameters, self.history)
        self.movement = Movement(
            self.parameters, self.history, self.physics, self.helpers
        )
        self.controllers = Controllers(
            self.parameters, self.history, self.physics, self.helpers, controller_parameters
        )
        self.plotting = Plotting(
            self.visual, self.parameters, self.history, self.helpers, self.controllers
        )
        self.determine_winner = DetermineWinner(self.helpers, self.plotting)

        self.animation = Animation(
            self.visual,
            self.parameters,
            self.history,
            self.movement,
            self.controllers,
            self.plotting,
            self.determine_winner,
        )
        self.animation.run()


game = FirstStrike()
game.play()
