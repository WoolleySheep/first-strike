from animation import Animation
from controllers import Controllers
from game_parameters import process_game_parameters
from plotting import Plotting
from result import Result


def play():

    (
        controller_parameters,
        visual,
        parameters,
        history,
    ) = process_game_parameters()
    controllers = Controllers(
        parameters,
        history,
        controller_parameters,
    )
    result = Result(parameters, history, controllers)
    plotting = Plotting(
        visual,
        parameters,
        history,
        controllers,
        result,
    )
    animation = Animation(
        visual,
        parameters,
        history,
        controllers,
        plotting,
        result,
    )
    animation.run()


# Uncomment to run the game normally
play()

# Uncomment to profile the code
# import cProfile
# import pstats
# import os

# modules2exclude = ("game.py", "animation.py", "plotting.py", "__init__.py", "__pycache__")
# modules = os.listdir("first_strike")
# modules2include = set(modules) - set(modules2exclude)
# additional = ("rocket_controller.py", "turret_controller.py")
# modules2include.update(additional)

# regex = r'|'.join([f"^{m}" for m in modules2include])

# cProfile.run("play()", "profile.dat")

# with open("profile.txt", "w") as f:
#     p = pstats.Stats("profile.dat", stream=f)
#     p.strip_dirs()
#     p.sort_stats("tottime").print_stats(regex)

# os.remove("profile.dat")
