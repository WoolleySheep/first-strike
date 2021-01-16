import math

from coordinate_classes import PolarCoordinate
from game_classes import ProjectileHistory
from game_helpers import is_within_bounds, has_hit_obstacle
from math_helpers import normalise_angle
from rocket_physics import (
    calc_rocket_velocity,
    calc_rocket_acceleration,
    calc_rocket_angular_velocity,
    calc_rocket_angular_acceleration,
    calc_main_engine_acceleration,
    calc_thruster_acceleration,
    calc_thruster_angular_acceleration,
)


def move_objects(self):

    move_the_rocket(self)

    move_projectiles(self)
    mark_projectiles_off_board(self)

    if should_fire_a_projectile(self):
        fire_a_projectile(self)

    rotate_the_turret(self)

    update_the_time(self)


def move_the_rocket(self):

    timestep = self.parameters.time.timestep

    rocket_vel = calc_rocket_velocity(self)
    rocket_ang_vel = calc_rocket_angular_velocity(self)
    main_engine_acc = calc_main_engine_acceleration(self)
    thrusters = self.parameters.animation.thruster_labels
    thrusters_acc = [
        calc_thruster_acceleration(self, thruster) for thruster in thrusters
    ]
    thrusters_ang_acc = [
        calc_thruster_angular_acceleration(self, thruster) for thruster in thrusters
    ]

    acc = main_engine_acc + sum(thrusters_acc)
    ang_acc = sum(thrusters_ang_acc)

    updated_vel = rocket_vel + acc * timestep
    updated_ang_vel = rocket_ang_vel + ang_acc * timestep

    locations = self.history.rocket.locations
    locations.append(locations[-1] + updated_vel * timestep)

    angles = self.history.rocket.angles
    angles.append(angles[-1] + updated_ang_vel * timestep)


def move_projectiles(self):

    timestep = self.parameters.time.timestep
    projectile_speed = self.parameters.turret.projectile_speed
    projectiles = self.history.projectiles

    for projectile in projectiles:
        if not projectile.on_board:
            continue

        firing_angle = projectile.firing_angle
        locations = projectile.locations
        location = locations[-1]
        delta = PolarCoordinate(projectile_speed * timestep, firing_angle).pol2cart()
        locations.append(location + delta)


def mark_projectiles_off_board(self):

    for projectile in self.history.projectiles:
        if not projectile.on_board:
            continue

        if not is_within_bounds(self, projectile.location) or has_hit_obstacle(
            self, projectile.location
        ):
            projectile.on_board = False


def should_fire_a_projectile(self):

    last_fired = self.history.turret.last_fired
    current_time = self.history.time
    return last_fired and math.isclose(current_time, last_fired)


def fire_a_projectile(self):

    turret_location = self.parameters.turret.location
    launch_angle = self.history.turret.angle
    current_time = self.history.time

    self.history.projectiles.append(
        ProjectileHistory([turret_location], launch_angle, current_time, True)
    )


def rotate_the_turret(self):

    rotation_velocity = self.history.turret.rotation_velocity
    timestep = self.parameters.time.timestep

    d_theta = rotation_velocity * timestep

    angles = self.history.turret.angles
    updated_angle = normalise_angle(angles[-1] + d_theta)
    angles.append(updated_angle)


def update_the_time(self):

    timesteps = self.history.timesteps
    timestep_duration = self.parameters.time.timestep
    timesteps.append(timesteps[-1] + timestep_duration)
