from game_setup import game_data


def is_within_bounds(x, y):

    w = game_data.environment.width
    h = game_data.environment.height

    return -w / 2 <= x <= w / 2 and -h / 2 <= y <= h / 2


def has_sufficient_time_elapsed_since_last_shot():

    when_fired = game_data.history.turret_history.when_fired

    if not when_fired:
        return True

    current_time = game_data.history.timesteps[-1]
    min_firing_interval = game_data.properties.turret_properties.min_firing_interval

    return current_time - when_fired[-1] >= min_firing_interval


def does_projectile_impact():

    target_radius = game_data.properties.rocket_properties.target_radius
    rocket_location = game_data.history.rocket_history.locations[-1]

    for projectile_history in game_data.history.projectile_histories:
        projectile_location = projectile_history.locations[-1]
        if distance_between(rocket_location, projectile_location) <= target_radius:
            return True

    return False


def is_game_time_exceeded():

    current_time = game_data.history.timesteps[-1]
    max_game_time = game_data.environment.max_game_time
    timestep = game_data.environment.timestep

    return current_time > max_game_time - timestep
