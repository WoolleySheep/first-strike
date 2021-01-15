from game_helpers import (
    does_rocket_impact_turret,
    does_projectile_impact_rocket,
    is_rocket_within_bounds,
    is_game_time_exceeded,
)


def determine_winner(self):

    rocket_hit_turret = does_rocket_impact_turret(self)
    projectile_hit_rocket = does_projectile_impact_rocket(self)

    if not is_rocket_within_bounds(self):
        self.title = "TURRET WIN: The rocket has gone out-of-bounds"
    elif rocket_hit_turret and projectile_hit_rocket:
        self.title = "DRAW: The rocket and turret have destroyed each other"
    elif rocket_hit_turret:
        self.title = "ROCKET_WIN: The rocket has hit the tower"
    elif projectile_hit_rocket:
        self.title = "TURRET WIN: A projectile has hit the rocket"
    elif is_game_time_exceeded(self):
        self.title = "DRAW: Game time exceeded"
