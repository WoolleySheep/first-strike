from animation import Animation
from meta_controller import Controllers
from helpers import Helpers
from movement import Movement
from game_parameters import process_game_parameters
from physics import Physics
from plotting import Plotting
from result import Result


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

        (
            controller_parameters,
            self.visual,
            self.parameters,
            self.history,
        ) = process_game_parameters()
        self.helpers = Helpers(self.parameters, self.history)
        self.physics = Physics(self.parameters, self.history)
        self.movement = Movement(
            self.parameters, self.history, self.physics, self.helpers
        )
        self.controllers = Controllers(
            self.parameters,
            self.history,
            self.physics,
            self.helpers,
            controller_parameters,
        )
        self.result = Result(
            self.parameters, self.history, self.helpers, self.controllers
        )
        self.plotting = Plotting(
            self.visual,
            self.parameters,
            self.history,
            self.helpers,
            self.controllers,
            self.result,
        )
        self.animation = Animation(
            self.visual,
            self.parameters,
            self.history,
            self.movement,
            self.controllers,
            self.plotting,
            self.result,
        )
        self.animation.run()


# Uncomment to run the game normally
FirstStrike().play()

# Uncomment to profile the code
# import cProfile
# import pstats
# import os

# modules2exclude = ("game.py", "animation.py", "plotting.py", "__init__.py")
# modules = os.listdir("first_strike")
# modules2include = set(modules) - set(modules2exclude)

# regex = r'|'.join([f"^{m}" for m in modules2include])

# cProfile.run("FirstStrike().play()", "profile.dat")

# with open("profile.txt", "w") as f:
#     p = pstats.Stats("profile.dat", stream=f)
#     p.strip_dirs()
#     p.sort_stats("cumtime").print_stats(regex)

# os.remove("profile.dat")
