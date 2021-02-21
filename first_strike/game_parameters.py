import json
import math

from history import (
    History,
    RocketHistory,
    TurretHistory,
)
from math_helpers import Coordinate
from parameters import (
    EnvironmentParameters,
    ObstacleParameters,
    Parameters,
    RocketParameters,
    TimeParameters,
    TurretParameters,
)
from visual import Visual


def process_game_parameters():

    game_parameters = _read_game_parameters()

    _validate_game_parameters(game_parameters)

    return _store_game_parameters(game_parameters)


def _is_colour(value):

    return value in ("b", "g", "r", "c", "m", "y", "k", "w")


def _read_game_parameters():

    with open("first_strike/game_parameters.json") as f:
        return json.load(f)


def _is_positive_float(value):

    return type(value) is float and value > 0


def _is_angle(angle):

    return type(angle) is float and -math.pi < angle <= math.pi


def _is_list_type(my_list, length, element_type):

    return (
        type(my_list) is list
        and len(my_list) == length
        and all((type(e) is element_type for e in my_list))
    )


def _is_location(location, w, h):

    return _is_list_type(location, 2, float) and _is_within_limits(location, w, h)


def _is_obstacle(location, radius, w, h):

    return _is_location(location, w, h) and _is_positive_float(radius)


def _is_within_limits(location, w, h):

    return (-w / 2 <= location[0] <= w / 2) and (-h / 2 <= location[1] <= h / 2)


def _validate_game_parameters(game_params):

    controllers = game_params["controllers"]
    assert controllers["rocket_active_controller"] in ["default", "player"]
    assert controllers["turret_active_controller"] in ["default", "player"]
    assert type(controllers["rocket_raise_errors"]) is bool
    assert type(controllers["turret_raise_errors"]) is bool

    visual = game_params["visual"]
    assert _is_positive_float(visual["fps"])
    assert _is_positive_float(visual["barrel_length_turret_radius_ratio"])
    assert _is_positive_float(visual["rocket_length_engine_bridge_width_ratio"])
    assert _is_positive_float(visual["rocket_length_max_thrust_length_ratio"])
    assert (
        _is_positive_float(visual["thrust_cone_angle"])
        and visual["thrust_cone_angle"] < math.pi / 2
    )
    assert (
        _is_positive_float(visual["game_over_alpha"]) and visual["game_over_alpha"] <= 1
    )
    assert type(visual["default_title"]) is str
    assert _is_colour(visual["rocket_colour"])
    assert _is_colour(visual["thrust_cone_colour"])
    assert _is_colour(visual["turret_colour"])
    assert _is_colour(visual["projectile_colour"])
    assert _is_colour(visual["obstacle_colour"])
    assert _is_colour(visual["not_ready2fire_colour"])
    assert _is_colour(visual["ready2fire_colour"])

    environment = game_params["environment"]
    assert _is_positive_float(environment["width"])
    assert _is_positive_float(environment["height"])

    if environment["obstacles"]:
        assert all(
            (
                _is_obstacle(
                    obstacle["location"],
                    obstacle["radius"],
                    environment["width"],
                    environment["height"],
                )
                for obstacle in environment["obstacles"]
            )
        )
    else:
        assert environment["obstacles"] is None

    time = game_params["time"]
    assert _is_positive_float(time["timestep"])
    assert _is_positive_float(time["max_game_time"])

    rocket = game_params["rocket"]
    assert _is_positive_float(rocket["mass"])
    assert _is_positive_float(rocket["length"])
    assert _is_positive_float(rocket["max_main_engine_force"])
    assert _is_positive_float(rocket["max_thruster_force"])
    assert _is_location(
        rocket["start_location"], environment["width"], environment["height"]
    )
    assert _is_angle(rocket["start_angle"])

    turret = game_params["turret"]
    assert _is_location(turret["location"], environment["width"], environment["height"])
    assert _is_angle(turret["start_angle"])
    assert _is_positive_float(turret["radius"])
    assert _is_positive_float(turret["max_rotation_speed"])
    assert _is_positive_float(turret["projectile_speed"])
    assert _is_positive_float(turret["min_firing_interval"])

    assert (
        time["max_game_time"] > time["timestep"]
    )  # Game cannot be shorter than 1 timestep
    assert (
        Coordinate(rocket["start_location"]).distance2(Coordinate(turret["location"]))
        > turret["radius"] + rocket["length"] / 2
    )  # Rocket cannot be already hitting turret

    if environment["obstacles"]:
        assert all(
            (
                Coordinate(rocket["start_location"]).distance2(
                    Coordinate(obstacle["location"])
                )
                > obstacle["radius"] + rocket["length"] / 2
                for obstacle in environment["obstacles"]
            )
        )  # Rocket cannot already be hitting any obstacle
        assert all(
            (
                Coordinate(turret["location"]).distance2(
                    Coordinate(obstacle["location"])
                )
                > obstacle["radius"] + turret["radius"]
                for obstacle in environment["obstacles"]
            )
        )  # Turret cannot be hitting any obstacle


def _store_game_parameters(game_params):

    controllers = game_params["controllers"]
    controller_parameters = (
        controllers["rocket_active_controller"],
        controllers["turret_active_controller"],
        controllers["rocket_raise_errors"],
        controllers["turret_raise_errors"],
    )

    visual = game_params["visual"]
    visual_obj = Visual(
        visual["fps"],
        visual["barrel_length_turret_radius_ratio"],
        visual["rocket_length_engine_bridge_width_ratio"],
        visual["rocket_length_max_thrust_length_ratio"],
        visual["thrust_cone_angle"],
        visual["game_over_alpha"],
        visual["default_title"],
        visual["rocket_colour"],
        visual["thrust_cone_colour"],
        visual["turret_colour"],
        visual["projectile_colour"],
        visual["obstacle_colour"],
        visual["not_ready2fire_colour"],
        visual["ready2fire_colour"],
    )

    environment = game_params["environment"]
    if environment["obstacles"]:
        obstacles = [
            ObstacleParameters(Coordinate(obstacle["location"]), obstacle["radius"])
            for obstacle in environment["obstacles"]
        ]
    else:
        obstacles = []
    environment_obj = EnvironmentParameters(
        environment["width"], environment["height"], obstacles
    )

    time = game_params["time"]
    time_obj = TimeParameters(time["timestep"], time["max_game_time"])

    rocket_params = game_params["rocket"]
    rocket_params_obj = RocketParameters(
        rocket_params["mass"],
        rocket_params["length"],
        rocket_params["max_main_engine_force"],
        rocket_params["max_thruster_force"],
    )

    turret_params = game_params["turret"]
    turret_location = Coordinate(turret_params["location"])
    turret_params_obj = TurretParameters(
        turret_params["radius"],
        turret_location,
        turret_params["max_rotation_speed"],
        turret_params["projectile_speed"],
        turret_params["min_firing_interval"],
    )

    parameters = Parameters(
        environment_obj, time_obj, rocket_params_obj, turret_params_obj
    )

    rocket_history_obj = RocketHistory(
        [Coordinate(rocket_params["start_location"])], [rocket_params["start_angle"]]
    )
    turret_history_obj = TurretHistory([turret_params["start_angle"]])

    history = History(rocket_history_obj, turret_history_obj)

    return controller_parameters, visual_obj, parameters, history
