import math, random

class Mobile:
    def __init__(self, options):
        self.options = options

        self.player = False
        self.bot = False

        self.health = 1

        self.id = str(random.random())

        self.chunkPos = False

        self.pos = options["pos"]
        self.vel = [0,0]
        self.friction = options["friction"] if self.options.get("friction") else 0.03

        self.radius = options["radius"]

        self.build = options["build"]
        self.build["maxHealth"] *= 0.1

        self.team = options["team"]

        self.rotation = 0

        self.duration = 99999999999

    

class Player(Mobile):
    def __init__(self, options):
        Mobile.__init__(self, options)

        self.player = True

        self.keys = {}
        self.controls = ["KeyW","KeyS","KeyA","KeyD"]#options.keys

        