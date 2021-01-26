class DetermineWinner:
    def __init__(self, helpers, plotting):
        self.helpers = helpers
        self.plotting = plotting

    def check_win_conditions(self):

        rocket_hit_turret = self.helpers.does_rocket_impact_turret()
        projectile_hit_rocket = self.helpers.does_projectile_impact_rocket()

        if not self.helpers.is_rocket_within_bounds():
            self.plotting.title = "TURRET WIN: The rocket has gone out-of-bounds"
        elif self.helpers.has_rocket_hit_obstacle():
            self.plotting.title = "TURRET WIN: The rocket has struck an obstacle"
        elif rocket_hit_turret and projectile_hit_rocket:
            self.plotting.title = (
                "DRAW: The rocket and turret have destroyed each other"
            )
        elif rocket_hit_turret:
            self.plotting.title = "ROCKET_WIN: The rocket has hit the tower"
        elif projectile_hit_rocket:
            self.plotting.title = "TURRET WIN: A projectile has hit the rocket"
        elif self.helpers.is_game_time_exceeded():
            self.plotting.title = "DRAW: Game time exceeded"
