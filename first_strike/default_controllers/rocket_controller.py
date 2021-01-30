import math

from controller import Controller
from coordinate_classes import Coordinate, PolarCoordinate
from math_helpers import (
    normalise_angle,
    distance_between_coordinates,
    RelativeObjects,
    average,
)


class RocketController(Controller):
    def __init__(self, parameters, history, physics, helpers):
        super().__init__(parameters, history, physics, helpers)

    def _calc_turret_attraction(self):

        min_turret_pull = 0.005

        attraction_angle = self.controller_helpers.calc_angle2turret_relative2rocket()

        dist2turret = self.controller_helpers.calc_dist_between_rocket_and_turret()
        turret_radius = self.parameters.turret.target_radius
        rocket_radius = self.parameters.rocket.target_radius

        attraction_strength = 1 / (dist2turret - rocket_radius - turret_radius)

        return PolarCoordinate(
            max(min_turret_pull, attraction_strength), attraction_angle
        ).pol2cart()

    @staticmethod
    def _calc_edge_repulsion(position, boundary):
        try:
            left_repulsion = 1 / (boundary / 2 + position)
        except ZeroDivisionError:  # Sitting on left boundary
            return float("inf")

        try:
            right_repulsion = -1 / (boundary / 2 - position)
        except ZeroDivisionError:  # Sitting on right boundary
            return -float("inf")

        return left_repulsion + right_repulsion

    def _calc_edge_avoidance(self):

        rocket_location = self.history.rocket.location
        width = self.parameters.environment.width
        height = self.parameters.environment.height

        return Coordinate(
            self._calc_edge_repulsion(rocket_location.x, width),
            self._calc_edge_repulsion(rocket_location.y, height),
        )

    def _calc_obstacle_avoidance(self):

        rocket_location = self.history.rocket.location

        obstacle_avoidance = []
        for obstacle in self.parameters.environment.obstacles:
            delta = rocket_location - obstacle.location
            avoidance_strength = 1 / (
                delta.magnitude - obstacle.radius - self.parameters.rocket.target_radius
            )
            obstacle_avoidance.append(
                PolarCoordinate(
                    avoidance_strength,
                    delta.angle,
                ).pol2cart()
            )

        if not obstacle_avoidance:
            return Coordinate(0.0, 0.0)
        return average(obstacle_avoidance)

    def _calc_projectile_avoidance(self):

        rocket_location = self.history.rocket.location

        projectile_avoidance = []
        for projectile in self.history.active_projectiles:
            delta = rocket_location - self.helpers.calc_projectile_location(projectile)
            avoidance_strength = 1 / (
                delta.magnitude - self.parameters.rocket.target_radius
            )
            projectile_avoidance.append(
                PolarCoordinate(avoidance_strength, delta.angle).pol2cart()
            )

        if not projectile_avoidance:
            return Coordinate(0.0, 0.0)

        return average(projectile_avoidance)

    def _calc_intersecting_obstacle_avoidance(self):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        intersecting_obstacle_avoidance = []
        for obstacle in self.parameters.environment.obstacles:
            rocket2obstacle = RelativeObjects(
                rocket_location, obstacle.location, rocket_velocity
            )
            (
                min_dist,
                _,
                (rocket_location_min_dist, _),
            ) = rocket2obstacle.minimum_distance_between_objects()
            threshold = self.parameters.rocket.target_radius + obstacle.radius
            if min_dist <= threshold and self.helpers.is_within_bounds(
                rocket_location_min_dist
            ):
                _, (
                    rocket_location_thresh_dist,
                    _,
                ) = rocket2obstacle.distance_between_objects_first_occurs(threshold)
                dist2threshold = distance_between_coordinates(
                    rocket_location, rocket_location_thresh_dist
                )
                try:
                    avoidance_strength = obstacle.radius / (min_dist * dist2threshold)
                except ZeroDivisionError:
                    avoidance_strength = float("inf")
                avoidance_angle = (rocket_location_min_dist - obstacle.location).angle
                intersecting_obstacle_avoidance.append(
                    PolarCoordinate(avoidance_strength, avoidance_angle).pol2cart()
                )

        if not intersecting_obstacle_avoidance:
            return Coordinate(0.0, 0.0)
        return average(intersecting_obstacle_avoidance)

    def _calc_intersecting_projectile_avoidance(self):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        intersecting_projectile_avoidance = []
        for projectile in self.history.active_projectiles:
            projectile_location = self.helpers.calc_projectile_location(projectile)
            projectile_velocity = self.helpers.calc_projectile_velocity(projectile)
            rocket2projectile = RelativeObjects(
                rocket_location,
                projectile_location,
                rocket_velocity,
                projectile_velocity,
            )
            (
                min_dist,
                _,
                (rocket_location_min_dist, projectile_location_min_dist),
            ) = rocket2projectile.minimum_distance_between_objects()
            threshold = self.parameters.rocket.target_radius
            if (
                min_dist <= threshold
                and self.helpers.is_within_bounds(rocket_location_min_dist)
                and self.helpers.is_within_bounds(projectile_location_min_dist)
            ):
                _, (
                    rocket_location_thresh_dist,
                    _,
                ) = rocket2projectile.distance_between_objects_first_occurs(threshold)
                dist2threshold = distance_between_coordinates(
                    rocket_location, rocket_location_thresh_dist
                )
                try:
                    avoidance_strength = 1 / (min_dist * dist2threshold)
                except ZeroDivisionError:
                    avoidance_strength = float("inf")
                avoidance_angle = (
                    rocket_location_min_dist - projectile_location_min_dist
                ).angle
                intersecting_projectile_avoidance.append(
                    PolarCoordinate(avoidance_strength, avoidance_angle).pol2cart()
                )

        if not intersecting_projectile_avoidance:
            return Coordinate(0.0, 0.0)
        return average(intersecting_projectile_avoidance)

    def _calc_within_buffer_obstacle_avoidance(self, safety_factor=2.0):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        within_buffer_obstacle_avoidance = []
        for obstacle in self.parameters.environment.obstacles:
            rocket2obstacle = RelativeObjects(
                rocket_location, obstacle.location, rocket_velocity
            )
            (
                min_dist,
                _,
                (rocket_location_min_dist, _),
            ) = rocket2obstacle.minimum_distance_between_objects()
            buffer = safety_factor * (
                self.parameters.rocket.target_radius + obstacle.radius
            )
            if min_dist <= buffer and self.helpers.is_within_bounds(
                rocket_location_min_dist
            ):
                try:
                    avoidance_strength = 1 / min_dist
                except ZeroDivisionError:
                    avoidance_strength = float("inf")
                avoidance_angle = (rocket_location_min_dist - obstacle.location).angle
                within_buffer_obstacle_avoidance.append(
                    PolarCoordinate(avoidance_strength, avoidance_angle).pol2cart()
                )

        if not within_buffer_obstacle_avoidance:
            return Coordinate(0.0, 0.0)
        return average(within_buffer_obstacle_avoidance)

    def _calc_within_buffer_projectile_avoidance(self, safety_factor=2.0):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        within_buffer_projectile_avoidance = []
        for projectile in self.history.active_projectiles:
            projectile_location = self.helpers.calc_projectile_location(projectile)
            projectile_velocity = self.helpers.calc_projectile_velocity(projectile)
            rocket2projectile = RelativeObjects(
                rocket_location,
                projectile_location,
                rocket_velocity,
                projectile_velocity,
            )
            (
                min_dist,
                _,
                (rocket_location_min_dist, projectile_location_min_dist),
            ) = rocket2projectile.minimum_distance_between_objects()
            buffer = safety_factor * self.parameters.rocket.target_radius
            if (
                min_dist <= buffer
                and self.helpers.is_within_bounds(rocket_location_min_dist)
                and self.helpers.is_within_bounds(projectile_location_min_dist)
            ):
                current_dist = (
                    self.controller_helpers.calc_dist_between_rocket_and_projectile(
                        projectile
                    )
                )
                try:
                    avoidance_strength = 1 / (
                        min_dist * (current_dist - self.parameters.rocket.target_radius)
                    )
                except ZeroDivisionError:
                    avoidance_strength = float("inf")
                avoidance_angle = (
                    rocket_location_min_dist - projectile_location_min_dist
                ).angle
                within_buffer_projectile_avoidance.append(
                    PolarCoordinate(avoidance_strength, avoidance_angle).pol2cart()
                )

        if not within_buffer_projectile_avoidance:
            return Coordinate(0.0, 0.0)
        return average(within_buffer_projectile_avoidance)

    @staticmethod
    def calc_minimum_distance_from_location2line(location, gradient, y_intercept):

        x, y = location.x, location.y

        a = 1 + gradient ** 2
        b = 2 * (gradient * (y_intercept - y) - x)
        c = x ** 2 + (y_intercept - y) ** 2

        line_x_min_dist = -b / (2 * a)
        line_y_min_dist = gradient * line_x_min_dist + y_intercept
        line_location_min_dist = Coordinate(line_x_min_dist, line_y_min_dist)

        return distance_between_coordinates(location, line_location_min_dist)

    def _calc_projectile_path_avoidance(self):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()
        turret_location = self.parameters.turret.location

        projectile_path_avoidance = []
        for projectile in self.history.active_projectiles:
            gradient = math.tan(projectile.firing_angle)
            y_intercept = turret_location.y - gradient * turret_location.x
            y_value = gradient * rocket_location.x + y_intercept
            avoidance_angle = normalise_angle(
                projectile.firing_angle
                + (1 if rocket_location.y > y_value else -1) * math.pi / 2
            )
            min_dist_rocket2path = self.calc_minimum_distance_from_location2line(
                rocket_location, gradient, y_intercept
            )
            projectile_location = self.helpers.calc_projectile_location(projectile)
            dist_rockt2projectile = distance_between_coordinates(
                rocket_location, projectile_location
            )
            try:
                avoidance_strength = 1 / (
                    min_dist_rocket2path
                    * (dist_rockt2projectile - self.parameters.rocket.target_radius)
                )
            except ZeroDivisionError:
                avoidance_strength = float("inf")
            projectile_path_avoidance.append(
                PolarCoordinate(avoidance_strength, avoidance_angle).pol2cart()
            )

        if not projectile_path_avoidance:
            return Coordinate(0.0, 0.0)
        return average(projectile_path_avoidance)

    def _calc_recharge_factor(self):
        """1 if ready to fire, 0 if just fired"""

        last_fired = self.history.turret.last_fired

        if not last_fired:
            return 1.0

        dtime = self.history.time - last_fired
        min_firing_interval = self.parameters.turret.min_firing_interval

        return min(1.0, dtime / min_firing_interval)

    def _calc_angle_turret_barrel2rocket(self):

        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location
        turret_angle = self.history.turret.angle

        angle_turret2rocket = (rocket_location - turret_location).angle

        return normalise_angle(angle_turret2rocket - turret_angle)

    def _calc_rotation_factor(self):
        """1 if aligned with intercept angle, 0 if pointing in the opposite direction"""

        intercept_angle = self.controller_helpers.firing_angle2hit_rocket()
        if intercept_angle is None:  # Moving too fast to hit
            return 0.0

        angle_turret_barrel2rocket = normalise_angle(
            intercept_angle - self.history.turret.angle
        )

        return 1 - abs(angle_turret_barrel2rocket) / math.pi

    def _calc_firing_path_avoidance(self):

        rocket_location = self.history.rocket.location
        turret_location = self.parameters.turret.location

        recharge_factor = self._calc_recharge_factor()
        rotation_factor = self._calc_rotation_factor()

        turret_angle = self.history.turret.angle
        gradient = math.tan(turret_angle)
        y_intercept = turret_location.y - gradient * turret_location.x
        y_value = gradient * rocket_location.x + y_intercept
        avoidance_angle = normalise_angle(
            turret_angle + (1 if rocket_location.y > y_value else -1) * math.pi / 2
        )
        min_dist_rocket2path = self.calc_minimum_distance_from_location2line(
            rocket_location, gradient, y_intercept
        )
        dist_rockt2projectile = (
            self.controller_helpers.calc_dist_between_rocket_and_turret()
        )
        return PolarCoordinate(
            rotation_factor
            * recharge_factor
            / (min_dist_rocket2path * dist_rockt2projectile),
            avoidance_angle,
        ).pol2cart()

    def _calc_direction(self, safety_buffer=2.0):

        turret_attraction_factor = 40
        edge_avoidance_factor = 20
        obstacle_avoidance_factor = 25.0
        projectile_avoidance_factor = 5.0
        intersecting_obstacle_avoidance_factor = 100
        intersecting_projectile_avoidance_factor = 100
        within_buffer_obstacle_avoidance_factor = 15
        within_buffer_projectile_avoidance_factor = 15

        projectile_path_avoidance_factor = 2
        firing_path_avoidance_factor = 4

        turret_attraction = self._calc_turret_attraction()
        edge_avoidance = self._calc_edge_avoidance()
        obstacle_avoidance = self._calc_obstacle_avoidance()
        projectile_avoidance = self._calc_projectile_avoidance()
        intersecting_obstacle_avoidance = self._calc_intersecting_obstacle_avoidance()
        intersecting_projectile_avoidance = (
            self._calc_intersecting_projectile_avoidance()
        )
        within_buffer_obstacle_avoidance = self._calc_within_buffer_obstacle_avoidance(
            safety_buffer
        )
        within_buffer_projectile_avoidance = (
            self._calc_within_buffer_projectile_avoidance(safety_buffer)
        )
        projectile_path_avoidance = self._calc_projectile_path_avoidance()
        firing_path_avoidance = self._calc_firing_path_avoidance()

        return (
            turret_attraction_factor * turret_attraction
            + edge_avoidance_factor * edge_avoidance
            + obstacle_avoidance_factor * obstacle_avoidance
            + projectile_avoidance_factor * projectile_avoidance
            + intersecting_obstacle_avoidance_factor * intersecting_obstacle_avoidance
            + intersecting_projectile_avoidance_factor
            * intersecting_projectile_avoidance
            + within_buffer_obstacle_avoidance_factor * within_buffer_obstacle_avoidance
            + within_buffer_projectile_avoidance_factor
            * within_buffer_projectile_avoidance
            + projectile_path_avoidance_factor * projectile_path_avoidance
            + firing_path_avoidance_factor * firing_path_avoidance
        )

    def is_within_buffer(self, safety_buffer=2.0):

        rocket_location = self.history.rocket.location
        rocket_velocity = self.physics.calc_rocket_velocity()

        for obstacle in self.parameters.environment.obstacles:
            threshold = safety_buffer * (
                self.parameters.rocket.target_radius + obstacle.radius
            )
            if (
                distance_between_coordinates(rocket_location, obstacle.location)
                <= threshold
            ):
                rocket2obstacle = RelativeObjects(
                    rocket_location, obstacle.location, rocket_velocity
                )
                min_dist, *_ = rocket2obstacle.minimum_distance_between_objects()
                if min_dist <= self.parameters.rocket.target_radius + obstacle.radius:
                    return True

        threshold = safety_buffer * self.parameters.rocket.target_radius
        for projectile in self.history.projectiles:
            projectile_location = self.helpers.calc_projectile_location(projectile)
            if (
                distance_between_coordinates(rocket_location, projectile_location)
                <= threshold
            ):
                projectile_velocity = self.helpers.calc_projectile_velocity(projectile)
                rocket2projectile = RelativeObjects(
                    rocket_location,
                    projectile_location,
                    rocket_velocity,
                    projectile_velocity,
                )
                min_dist, *_ = rocket2projectile.minimum_distance_between_objects()
                if min_dist <= self.parameters.rocket.target_radius:
                    return True

        if (
            self.parameters.environment.width / 2 - abs(rocket_location.x) <= threshold
            or self.parameters.environment.height / 2 - abs(rocket_location.y)
            <= threshold
        ):
            return True

        return False

    def calc_inputs(self):

        safety_buffer = 2.0

        direction = self._calc_direction(safety_buffer)

        # Current velocity
        rocket_velocity = self.physics.calc_rocket_velocity()
        rocket_vel_angle = rocket_velocity.angle

        direction_velocity_ratio = 140.0

        thrust_direction = direction_velocity_ratio * direction - rocket_velocity
        thrust_angle = thrust_direction.angle

        rocket_angle = self.history.rocket.angle
        relative_thrust_angle = normalise_angle(thrust_angle - rocket_angle)

        # If facing away from the turret, spin the rocket using the thrusters
        # Use PD controller
        p_c = 0.75
        d_c = -0.35

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

        max_outputs = [self.parameters.rocket.max_main_engine_force] + [
            max_thruster_force
        ] * 4
        remaining_outputs = [
            max_thrust - rotational_thrust
            for max_thrust, rotational_thrust in zip(max_outputs, rotational_outputs)
        ]

        if self.is_within_buffer(safety_buffer):
            if not math.isclose(relative_thrust_angle, 0) and not math.isclose(
                relative_thrust_angle, math.pi
            ):
                idx1, idx2 = (3, 4) if relative_thrust_angle > 0 else (1, 2)
                min_remaining_thruster_output = min(
                    remaining_outputs[idx1], remaining_outputs[idx2]
                )
                for idx in (idx1, idx2):
                    rotational_outputs[idx] += min_remaining_thruster_output

            if abs(relative_thrust_angle) < 3 * math.pi / 4:
                rotational_outputs[0] = self.parameters.rocket.max_main_engine_force

            return rotational_outputs

        if abs(relative_thrust_angle) > math.pi / 2:
            return rotational_outputs

        left_thrusters_active = relative_thrust_angle < 0
        right_thrusters_active = relative_thrust_angle >= 0
        thrusters_active = [left_thrusters_active] * 2 + [right_thrusters_active] * 2

        engine_translation_force_ratio = [math.cos(relative_thrust_angle)] + [
            active * abs(math.sin(relative_thrust_angle)) / 2
            for active in thrusters_active
        ]
        try:
            min_max_ratio = min(
                (
                    max_output / force_ratio
                    for max_output, force_ratio in zip(
                        max_outputs, engine_translation_force_ratio
                    )
                )
            )
        except ZeroDivisionError:
            min_max_ratio = min(
                (
                    max_output / force_ratio
                    for max_output, force_ratio in zip(
                        max_outputs, engine_translation_force_ratio
                    )
                    if not math.isclose(force_ratio, 0.0)
                )
            )
        translation_engine_forces = [
            min_max_ratio * force_ratio
            for force_ratio in engine_translation_force_ratio
        ]

        try:

            max_output_ratio = max(
                (
                    output / remaining
                    for output, remaining in zip(
                        translation_engine_forces, remaining_outputs
                    )
                )
            )
        except ZeroDivisionError:  # Remaining thrust is 0; cannot manouver directionally
            return rotational_outputs

        directional_outputs = [
            output / max_output_ratio for output in translation_engine_forces
        ]

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
