from game_data import (
    Environment,
    RocketProperties,
    TurretProperties,
    Properties,
    RocketHistory,
    TurretHistory,
    History,
    GameData,
)

WIDTH = 200.0
HEIGHT = 200.0
TIMESTEP = 0.1
MAX_GAME_TIME = 120

MASS = 100.0
ROCKET_TARGET_RADIUS = 5.0
ROCKET_LENGTH = 5.0
MAX_MAIN_ENGINE_FORCE = 100.0
MAX_THRUSTER_FORCE = 20.0

TURRET_TARGET_RADIUS = 5.0
TURRET_LOCATION = (0.0, 0.0)
MAX_ROTATION_SPEED = 1.0
PROJECTILE_SPEED = 45.0
MIN_FIRING_INTERVAL = 3.0

ROCKET_START_LOCATION = (-100.0, 50.0)
ROCKET_START_ANGLE = 0.0

TURRET_START_ANGLE = 0.0

environment = Environment(WIDTH, HEIGHT, TIMESTEP, MAX_GAME_TIME)

rocket_properties = RocketProperties(
    MASS,
    ROCKET_TARGET_RADIUS,
    ROCKET_LENGTH,
    MAX_MAIN_ENGINE_FORCE,
    MAX_THRUSTER_FORCE,
)
turret_properties = TurretProperties(
    TURRET_TARGET_RADIUS,
    TURRET_LOCATION,
    MAX_ROTATION_SPEED,
    PROJECTILE_SPEED,
    MIN_FIRING_INTERVAL,
)
properties = Properties(rocket_properties, turret_properties)

rocket_history = RocketHistory([ROCKET_START_LOCATION], [ROCKET_START_ANGLE])
turret_history = TurretHistory([TURRET_START_ANGLE])
history = History(rocket_history, turret_history)

game_data = GameData(environment, properties, history)
