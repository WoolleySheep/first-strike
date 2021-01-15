import json
import math

from game_classes import (
    AnimationParameters,
    EnvironmentParameters,
    TimeParameters,
    RocketParameters,
    TurretParameters,
    Parameters,
    RocketHistory,
    TurretHistory,
    History,
)
from coordinate_classes import Coordinate
from math_helpers import distance_between_coordinates


def process_game_parameters(self):

    game_parameters = _read_game_parameters()

    _validate_game_parameters(game_parameters)

    _store_game_parameters(self, game_parameters)


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
        and all([type(e) is element_type for e in my_list])
    )


def _is_location(location, w, h):

    return _is_list_type(location, 2, float) and _is_within_bounds(location, w, h)


def _is_within_bounds(location, w, h):

    return (-w / 2 <= location[0] <= w / 2) and (-h / 2 <= location[1] <= h / 2)


def _validate_game_parameters(game_params):

    # animation
    animation = game_params["animation"]
    assert _is_positive_float(animation["fps"])
    assert _is_positive_float(animation["square_root_board_area_barrel_length_ratio"])
    assert _is_positive_float(animation["rocket_length_engine_bridge_width_ratio"])
    assert _is_positive_float(animation["rocket_length_max_thrust_length_ratio"])
    assert (
        _is_positive_float(animation["thrust_cone_angle"])
        and animation["thrust_cone_angle"] < math.pi / 2
    )
    assert (
        _is_positive_float(animation["game_over_alpha"])
        and animation["game_over_alpha"] <= 1
    )
    assert type(animation["default_title"]) is str
    assert _is_list_type(animation["engine_labels"], 5, str)

    environment = game_params["environment"]
    assert _is_positive_float(environment["width"])
    assert _is_positive_float(environment["height"])

    time = game_params["time"]
    assert _is_positive_float(time["timestep"])
    assert _is_positive_float(time["max_game_time"])

    rocket = game_params["rocket"]
    assert _is_positive_float(rocket["mass"])
    assert _is_positive_float(rocket["target_radius"])
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
    assert _is_positive_float(turret["target_radius"])
    assert _is_positive_float(turret["max_rotation_speed"])
    assert _is_positive_float(turret["projectile_speed"])
    assert _is_positive_float(turret["min_firing_interval"])

    assert (
        time["max_game_time"] > time["timestep"]
    )  # Game cannot be shorter than 1 timestep
    assert (
        distance_between_coordinates(
            Coordinate(rocket["start_location"]), Coordinate(turret["location"])
        )
        > rocket["target_radius"]
    )
    assert (
        distance_between_coordinates(
            Coordinate(rocket["start_location"]), Coordinate(turret["location"])
        )
        > turret["target_radius"]
    )


def _store_game_parameters(self, game_params):

    animation = game_params["animation"]
    animation_obj = AnimationParameters(
        animation["fps"],
        animation["square_root_board_area_barrel_length_ratio"],
        animation["rocket_length_engine_bridge_width_ratio"],
        animation["rocket_length_max_thrust_length_ratio"],
        animation["thrust_cone_angle"],
        animation["game_over_alpha"],
        animation["default_title"],
        animation["engine_labels"],
    )

    environment = game_params["environment"]
    environment_obj = EnvironmentParameters(environment["width"], environment["height"])

    time = game_params["time"]
    time_obj = TimeParameters(time["timestep"], time["max_game_time"])

    rocket_params = game_params["rocket"]
    rocket_params_obj = RocketParameters(
        rocket_params["mass"],
        rocket_params["target_radius"],
        rocket_params["length"],
        rocket_params["max_main_engine_force"],
        rocket_params["max_thruster_force"],
    )

    turret_params = game_params["turret"]
    turret_location = Coordinate(turret_params["location"])
    turret_params_obj = TurretParameters(
        turret_params["target_radius"],
        turret_location,
        turret_params["max_rotation_speed"],
        turret_params["projectile_speed"],
        turret_params["min_firing_interval"],
    )

    self.parameters = Parameters(
        animation_obj, environment_obj, time_obj, rocket_params_obj, turret_params_obj
    )

    rocket_history_obj = RocketHistory(
        [Coordinate(rocket_params["start_location"])], [rocket_params["start_angle"]]
    )
    turret_history_obj = TurretHistory([turret_params["start_angle"]])

    self.history = History(rocket_history_obj, turret_history_obj)

    self.title = animation["default_title"]
