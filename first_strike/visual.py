from dataclasses import dataclass


@dataclass
class Visual:
    fps: float
    barrel_length_turret_radius_ratio: float
    rocket_length_engine_bridge_width_ratio: float
    rocket_length_max_thrust_length_ratio: float
    thrust_cone_angle: float
    game_over_alpha: float
    default_title: str
    rocket_colour: str
    thrust_cone_colour: str
    turret_colour: str
    projectile_colour: str
    obstacle_colour: str
    not_ready2fire_colour: str
    ready2fire_colour: str

    @property
    def frame_interval_ms(self) -> int:
        """Frame interval in ms"""
        return int(1000 / self.fps)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
