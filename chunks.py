import math

class Chunks:
    def __init__(self,options):
        self.options = options

        self.mainArray = {}

    def pos2ChunkPos(self, pos):
        return [
            math.floor(pos[0]/self.options.chunkSize[0]),
            math.floor(pos[1]/self.options.chunkSize[1]),
        ]
    def posStringify(self,pos):
        return f"{pos[0]}/{pos[1]}"

    def requestChunk(pos):
        posStr = self.posStringify(pos)
        if not self.mainArray.get(posStr):
            self.mainArray[posStr] = []

        return self.mainArray

    def instertMob(self, chunkPos, mob):
        self.mainArray[chunkPos]

    def evaluateMob(self, mob):
        if not mob.chunkPos:
            mob.chunkPos = self.posStringify(self.pos2ChunkPos(mob.pos))


        