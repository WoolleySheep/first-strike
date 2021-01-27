import math

from coordinate_classes import PolarCoordinate
from game_classes import ProjectileHistory
from math_helpers import normalise_angle


class Movement:
    def __init__(self, parameters, history, physics, helpers):
        self.parameters = parameters
        self.history = history
        self.physics = physics
        self.helpers = helpers

    def move_objects(self):

        self.move_the_rocket()

        self.mark_projectiles_off_board()

        if self.should_fire_a_projectile():
            self.fire_a_projectile()

        self.rotate_the_turret()

        self.update_the_time()

    def move_the_rocket(self):

        rocket_vel = self.physics.calc_rocket_velocity()
        rocket_ang_vel = self.physics.calc_rocket_angular_velocity()
        main_engine_acc = self.physics.calc_main_engine_acceleration()

        thrusters = self.parameters.animation.thruster_labels

        thrusters_acc = [
            self.physics.calc_thruster_acceleration(thruster) for thruster in thrusters
        ]
        thrusters_ang_acc = [
            self.physics.calc_thruster_angular_acceleration(thruster)
            for thruster in thrusters
        ]

        acc = main_engine_acc + sum(thrusters_acc)
        ang_acc = sum(thrusters_ang_acc)

        timestep = self.parameters.time.timestep

        updated_vel = rocket_vel + acc * timestep
        updated_ang_vel = rocket_ang_vel + ang_acc * timestep

        locations = self.history.rocket.locations
        locations.append(locations[-1] + updated_vel * timestep)

        angles = self.history.rocket.angles
        angles.append(angles[-1] + updated_ang_vel * timestep)

    def mark_projectiles_off_board(self):

        for projectile in self.history.projectiles:
            location = self.helpers.calc_projectile_location(projectile)
            if not projectile.on_board:
                continue

            projectile.on_board = self.helpers.is_within_bounds(
                location
            ) and not self.helpers.has_hit_obstacle(location)

    def should_fire_a_projectile(self):

        last_fired = self.history.turret.last_fired
        current_time = self.history.time
        return last_fired and math.isclose(current_time, last_fired)

    def fire_a_projectile(self):

        turret_location = self.parameters.turret.location
        launch_angle = self.history.turret.angle
        current_time = self.history.time

        self.history.projectiles.append(
            ProjectileHistory(launch_angle, current_time, True)
        )

    def rotate_the_turret(self):

        rotation_velocity = self.history.turret.rotation_velocity
        timestep = self.parameters.time.timestep

        d_theta = rotation_velocity * timestep

        angles = self.history.turret.angles
        angles.append(normalise_angle(angles[-1] + d_theta))
        # TODO: For some reason these values are not always normalised

    def update_the_time(self):

        timesteps = self.history.timesteps
        timestep_duration = self.parameters.time.timestep
        timesteps.append(timesteps[-1] + timestep_duration)
