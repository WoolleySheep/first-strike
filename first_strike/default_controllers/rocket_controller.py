import math

from controller import Controller
from coordinate_classes import Coordinate, PolarCoordinate
from math_helpers import normalise_angle, distance_between_coordinates


class RocketController(Controller):
    def __init__(self, parameters, history, physics, helpers):
        super().__init__(parameters, history, physics, helpers)

    def _calc_turret_attraction(self):

        dist2turret = self.controller_helpers.calc_dist_from_rocket2turret()
        angle2turret = self.controller_helpers.calc_angle_from_rocket2turret()
        turret_radius = self.parameters.turret.target_radius
        rocket_radius = self.parameters.rocket.target_radius
        return PolarCoordinate(
            1 / (dist2turret - rocket_radius - turret_radius), angle2turret
        ).pol2cart()

    def _calc_edge_avoidance(self):
        def edge_repulsion(position, boundary):
            try:
                left_repulsion = 1 / (boundary / 2 + position)
            except ZeroDivisionError:   # Sitting on left boundary
                return float('inf')

            try:
                right_repulsion = - 1 / (boundary / 2 - position)
            except ZeroDivisionError:   # Sitting on right boundary
                return -float('inf')

            return left_repulsion + right_repulsion

        rocket_location = self.history.rocket.location
        width = self.parameters.environment.width
        height = self.parameters.environment.height

        return Coordinate(
            edge_repulsion(rocket_location.x, width),
            edge_repulsion(rocket_location.y, height),
        )

    def _calc_all_projectile_path_avoidance(self):

        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location

        all_projectile_path_avoidance = Coordinate(0.0, 0.0)
        for projectile in self.history.active_projectiles:
            gradient = math.tan(projectile.firing_angle)
            y_value = (
                gradient * (rocket_location.x - turret_location.x) + turret_location.y
            )
            avoidance_angle = normalise_angle(
                projectile.firing_angle
                + (math.pi / 2) * (1 if rocket_location.y > y_value else 0)
            )
            dist = distance_between_coordinates(
                rocket_location, self.helpers.calc_projectile_location(projectile)
            )
            all_projectile_path_avoidance += PolarCoordinate(
                1 / (dist - self.parameters.rocket.target_radius), avoidance_angle
            ).pol2cart()

        return all_projectile_path_avoidance

    def _calc_all_obstacle_avoidance(self):

        rocket_location = self.history.rocket.location

        all_obstacle_avoidance = Coordinate(0.0, 0.0)
        for obstacle in self.parameters.environment.obstacles:
            delta = rocket_location - obstacle.location
            all_obstacle_avoidance += PolarCoordinate(
                1
                / (
                    delta.magnitude
                    - obstacle.radius
                    - self.parameters.rocket.target_radius
                ),
                delta.angle,
            ).pol2cart()

        return all_obstacle_avoidance

    def _calc_intersecting_projectile_avoidance(self):

        safety_buffer = 2.0

        intersecting_projectile_avoidance = Coordinate(0.0, 0.0)
        for projectile in self.history.active_projectiles:
            (
                _,
                dist,
                (rocket_loc, projectile_loc),
            ) = self.controller_helpers.calc_minimum_distance_between_rocket_and_projectile(
                projectile
            )
            if dist <= safety_buffer * self.parameters.rocket.target_radius:
                dist_between = self.controller_helpers.calc_dist_from_rocket2projectile(
                    projectile
                )
                angle = (rocket_loc - projectile_loc).angle
                intersecting_projectile_avoidance += PolarCoordinate(
                    1
                    / math.sqrt(
                        dist * (dist_between - self.parameters.rocket.target_radius)
                    ),
                    angle,
                ).pol2cart()

        return intersecting_projectile_avoidance

    def _calc_intersecting_obstacle_avoidance(self):

        safety_buffer = 2.0

        intersecting_obstacle_avoidance = Coordinate(0.0, 0.0)
        for obstacle in self.parameters.environment.obstacles:
            (
                _,
                dist,
                (rocket_loc, _),
            ) = self.controller_helpers.calc_minimum_distance_between_rocket_and_obstacle(
                obstacle
            )
            if dist <= safety_buffer * (
                obstacle.radius + self.parameters.rocket.target_radius
            ):
                dist_between = self.controller_helpers.calc_dist_from_rocket2obstacle(
                    obstacle
                )
                angle = (rocket_loc - obstacle.location).angle
                intersecting_obstacle_avoidance += PolarCoordinate(
                    1
                    / math.sqrt(
                        dist
                        * (
                            dist_between
                            - obstacle.radius
                            - self.parameters.rocket.target_radius
                        )
                    ),
                    angle,
                ).pol2cart()

        return intersecting_obstacle_avoidance

    def _calc_recharge_factor(self):
        """1 if ready to fire, 0 if just fired"""

        last_fired = self.history.turret.last_fired

        if not last_fired:
            return 0.0

        dtime = self.history.time - last_fired
        min_firing_interval = self.parameters.turret.min_firing_interval

        return max(0.0, min_firing_interval - dtime)

    def _calc_angle_turret_barrel2rocket(self):

        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location
        turret_angle = self.history.turret.angle

        angle_turret2rocket = (rocket_location - turret_location).angle

        return normalise_angle(angle_turret2rocket - turret_angle)

    def _calc_rotation_factor(self):
        """1 if perfectly aligned, 0 if pointing in the opposite direction"""

        angle_turret_barrel2rocket = self._calc_angle_turret_barrel2rocket()

        return 1 - abs(angle_turret_barrel2rocket) / math.pi

    def _calc_firing_path_avoidance(self):

        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location

        recharge_factor = self._calc_recharge_factor()
        rotation_factor = self._calc_rotation_factor()

        turret_angle = self.history.turret.angle
        gradient = math.tan(turret_angle)
        y_value = gradient * (rocket_location.x - turret_location.x) + turret_location.y
        avoidance_angle = normalise_angle(
            turret_angle + (math.pi / 2) * (1 if rocket_location.y > y_value else -1)
        )
        dist = self.controller_helpers.calc_dist_from_rocket2turret()
        return PolarCoordinate(
            rotation_factor * recharge_factor / dist, avoidance_angle
        ).pol2cart()

    def _calc_direction(self):

        turret_attraction_factor = 20
        edge_avoidance_factor = 7
        all_obstacle_avoidance_factor = 2
        all_projectile_path_avoidance_factor = 2
        intersecting_obstacle_avoidance_factor = 10
        intersecting_projectile_avoidance_factor = 10
        firing_path_avoidance_factor = 2

        turret_attraction = self._calc_turret_attraction()
        edge_avoidance = self._calc_edge_avoidance()
        all_obstacle_avoidance = self._calc_all_obstacle_avoidance()
        all_projectile_path_avoidance = self._calc_all_projectile_path_avoidance()
        intersecting_obstacle_avoidance = self._calc_intersecting_obstacle_avoidance()
        intersecting_projectile_avoidance = (
            self._calc_intersecting_projectile_avoidance()
        )
        firing_path_avoidance = self._calc_firing_path_avoidance()

        return (
            turret_attraction_factor * turret_attraction
            + edge_avoidance_factor * edge_avoidance
            + all_obstacle_avoidance_factor * all_obstacle_avoidance
            + all_projectile_path_avoidance_factor * all_projectile_path_avoidance
            + intersecting_projectile_avoidance_factor
            * intersecting_projectile_avoidance
            + intersecting_obstacle_avoidance_factor * intersecting_obstacle_avoidance
            + firing_path_avoidance_factor * firing_path_avoidance
        )

    def calc_inputs(self):

        direction = self._calc_direction()

        # Current velocity
        rocket_velocity = self.physics.calc_rocket_velocity()
        rocket_vel_angle = rocket_velocity.angle

        thrust_direction = (
            PolarCoordinate(1.0, direction.angle).pol2cart()
            - PolarCoordinate(1.0, rocket_vel_angle).pol2cart()
        )
        thrust_angle = thrust_direction.angle

        rocket_angle = self.history.rocket.angle
        relative_thrust_angle = normalise_angle(thrust_angle - rocket_angle)

        # If facing away from the turret, spin the rocket using the thrusters
        # Use PD controller
        p_c = 5.0
        d_c = -3.0

        # Derivative
        angular_vel = self.physics.calc_rocket_angular_velocity()

        control_signal = p_c * relative_thrust_angle + d_c * angular_vel

        max_thruster_force = self.parameters.rocket.max_thruster_force
        thruster_force = min(
            abs(control_signal) * max_thruster_force, max_thruster_force
        )

        clockwise_thrust = thruster_force if control_signal < 0 else 0.0
        anticlockwise_thrust = thruster_force if control_signal >= 0 else 0.0

        rotational_outputs = [
            0.0,
            clockwise_thrust,
            anticlockwise_thrust,
            anticlockwise_thrust,
            clockwise_thrust,
        ]

        if not (-math.pi / 2 <= relative_thrust_angle <= math.pi / 2):
            return rotational_outputs

        left_thrusters_active = relative_thrust_angle < 0
        right_thrusters_active = relative_thrust_angle >= 0
        thrusters_active = [left_thrusters_active] * 2 + [right_thrusters_active] * 2

        engine_translation_force_ratio = [math.cos(relative_thrust_angle)] + [active * abs(math.sin(relative_thrust_angle)) / 2 for active in thrusters_active]
        max_outputs = [self.parameters.rocket.max_main_engine_force] + [max_thruster_force] * 4
        try:
            engine_max_ratio = [max_output / force_ratio for max_output, force_ratio in zip (max_outputs, engine_translation_force_ratio)]
        except ZeroDivisionError:
            engine_max_ratio = [max_output / force_ratio for max_output, force_ratio in zip (max_outputs, engine_translation_force_ratio) if not math.isclose(force_ratio, 0.0)]
        min_max_ratio = min(engine_max_ratio)
        translation_engine_forces = [min_max_ratio * force_ratio for force_ratio in engine_translation_force_ratio]

        remaining_outputs = [
            max_thrust - rotational_thrust
            for max_thrust, rotational_thrust in zip(max_outputs, rotational_outputs)
        ]

        try:
            output_ratios = [
                output / remaining
                for output, remaining in zip(translation_engine_forces, remaining_outputs)
            ]
        except ZeroDivisionError:  # Remaining thrust is 0; cannot manouver directionally
            return rotational_outputs

        max_ratio = max(output_ratios)
        directional_outputs = [output / max_ratio for output in translation_engine_forces]

        return [
            rotation + direction
            for rotation, direction in zip(rotational_outputs, directional_outputs)
        ]

    def angle_to_turret(self):

        rocket_angle = self.history.rocket.angle

        angle = math.atan2(
            *list(self.parameters.turret.location - self.history.rocket.location)[::-1]
        )

        return normalise_angle(angle - rocket_angle)
