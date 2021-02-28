import math

from helpers import Helpers
from history import ProjectileHistory
from math_helpers import normalise_angle
from physics import Physics


class Movement:
    def __init__(self, parameters, history):
        self.parameters = parameters
        self.history = history
        self.physics = Physics(parameters, history)
        self.helpers = Helpers(parameters, history)

    def move_objects(self):

        self.move_the_rocket()

        self.mark_projectiles_off_board()

        if self.should_fire_a_projectile():
            self.fire_a_projectile()

        self.rotate_the_turret()

        self.update_the_time()

    def move_the_rocket(self):

        timestep = self.parameters.time.timestep

        rocket_hist = self.history.rocket
        rocket_params = self.parameters.rocket

        vel = self.physics.calc_rocket_velocity()
        acc_relative = self.parameters.rocket.calc_acc_relative2rocket(
            rocket_hist.engine_forces
        )

        acc = acc_relative.rotate_by(rocket_hist.angle - math.pi / 2)

        updated_vel = vel + acc * timestep

        rocket_hist.locations.append(rocket_hist.location + updated_vel * timestep)

        angular_vel = self.physics.calc_rocket_angular_velocity()
        angular_acc = rocket_params.calc_angular_acc(rocket_hist.thruster_forces)

        updated_angular_vel = angular_vel + angular_acc * timestep

        updated_angle = normalise_angle(
            rocket_hist.angle + updated_angular_vel * timestep
        )
        rocket_hist.angles.append(updated_angle)

    def mark_projectiles_off_board(self):

        for projectile in self.history.projectiles:
            location = self.helpers.calc_projectile_location(projectile)
            if not projectile.on_board:
                continue

            if not self.helpers.is_within_bounds(
                location
            ) or self.helpers.has_hit_obstacle(location):
                projectile.on_board = False

    def should_fire_a_projectile(self):

        last_fired = self.history.turret.last_fired
        current_time = self.history.time
        return last_fired and math.isclose(current_time, last_fired)

    def fire_a_projectile(self):

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

    def update_the_time(self):

        self.history.time += self.parameters.time.timestep
