import math

class Chunks:
    def __init__(self,options):
        self.options = options

        self.mainArray = {}

    def pos2ChunkPos(self, pos):
        return [
            math.floor(pos[0]/self.options["chunkSize"][0]),
            math.floor(pos[1]/self.options["chunkSize"][1]),
        ]
    def posStringify(self,pos):
        return f"{pos[0]}/{pos[1]}"

    def requestChunk(self, pos):
        posStr = self.posStringify(pos)
        if not self.mainArray.get(posStr):
            self.mainArray[posStr] = []

        return self.mainArray[posStr]

    def instertMob(self, chunkPos, mob):
        self.requestChunk(chunkPos).append(mob)
    def removeMob(self, chunkPos, mob):
        self.requestChunk(chunkPos).remove(mob)

    def evaluateMob(self, mob):
        if not mob.chunkPos:
            mob.chunkPos = self.pos2ChunkPos(mob.pos)
            self.instertMob(mob.chunkPos, mob)
            return 0

        newChunkPos = self.pos2ChunkPos(mob.pos)

        currentPos = self.posStringify(newChunkPos)
        mobPos = self.posStringify(mob.chunkPos)
        if currentPos != mobPos:
            self.removeMob(mob.chunkPos, mob)
            self.instertMob(newChunkPos, mob)
            mob.chunkPos = newChunkPos
            
    
    def getSurroundingChunks(self,pos,rad=1):
        retChunks = []

        for x in range(pos[0]-rad,pos[0]+rad):
            for y in range(pos[1]-rad,pos[1]+rad):
                retChunks.append(self.requestChunk([x,y]))
        return retChunks

    def getMobilesInChunks(chunks):
        retMobiles = []
        for i in chunks:
            for mob in i:
                retMobiles.append(mob)
        return retMobiles

    def getAllMobiles(self):
        retMobiles = []
        for i in self.mainArray:
            for mob in self.mainArray[i]:
                retMobiles.append(mob)
        return retMobiles


        