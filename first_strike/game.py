from animation import Animation


class FirstStrike:
    def __init__(self):
        self.parameters = None
        self.history = None
        self.animation = None

    from process_game_parameters import process_game_parameters

    def play(self):

        self.process_game_parameters()

        self.animation = Animation(self.parameters, self.history)
        self.animation.run()


game = FirstStrike()
game.play()
