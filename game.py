from mobile import Mobile

class Game:
    def __init__(self):
        self.gameState = {
            "mobiles":[],
            "players":[],
        }

    def getStateForClients(self):
        return self.gameState

    def addMobile(self, options):
        newMob = Mobile({
            "pos":[1,1],
            "radius":5,
        })

    def updateState(self):
        pass