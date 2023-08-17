class Mobile:
    def __init__(self, options):
        self.options = options

        pos = options["pos"]
        vel = [0,0]

        radius = options["radius"]