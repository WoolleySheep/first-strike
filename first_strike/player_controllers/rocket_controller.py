from controller import Controller


class RocketController(Controller):
    def __init__(self, parameters, history, physics, helpers):
        super().__init__(parameters, history, physics, helpers)

    def calc_inputs(self):

        raise NotImplementedError
