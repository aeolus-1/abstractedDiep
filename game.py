from mobile import Mobile
from chunks import Chunks
from bot import runBot
import math, json, random, copy

from mobile import *

class Game:
    def __init__(self):
        self.options = {
            
        }
        self.gameState = {
            "mobiles":[],
            "players":[],
        }
        self.BUILDS = json.load(open('builds.json'))

        self.chunks = Chunks({
            "chunkSize":[0.5,0.5],
        })

        if True:
            botMob = self.addMobile({
                "pos":[15,5],
                "radius":0.25,
                "build":self.BUILDS["starter"],

                "team":"#0f0",
            })
            
            botMob.bot = True
            #botMob.bot = True
            for x in range(0):
                botMob = self.addMobile({
                    "pos":[5,random.random()],
                    "radius":0.25,
                    "build":self.BUILDS["healer"],

                    "team":"#f00",
                })
                
                botMob.bot = True

    def runCommand(self, code):
        eval(code)
    def spawnRandomBot(self):
        botMob = self.addMobile({
            "pos":[(random.random()*20)-5,(random.random()*20)-5],
            "radius":0.25,
            "build":self.BUILDS[random.choice(list(self.BUILDS.keys()))],

            "team":["#f00","#0f0","#00f","#f66"][random.randrange(0,3)],
        })
        
        botMob.bot = True

    def fetchMobile(self, id):
        def filterC(a):
            return a.id==id
        mobs = list(filter(filterC,self.gameState["mobiles"]))

        if (len(mobs)>0):
            return mobs[0]
        else:
            raise "searched for mob that wasn't there"

    def getStateForClients(self, sid):
        state = {
            "mobiles":[],
            "players":[],
            "cameraPos":[0,0],
            "sight":100,
        }
        state["cameraPos"] = self.clients[sid]["mobile"].pos
        state["sight"] = self.clients[sid]["mobile"].build["sight"]
        totMobiles = self.chunks.getAllMobiles()

        for mob in totMobiles:
            if (mob.player):
                state["players"].append(Game.processMobDictForClient(copy.deepcopy(mob.__dict__)))
            else:
                state["mobiles"].append(Game.processMobDictForClient(copy.deepcopy(mob.__dict__)))

        return state

    def processMobDictForClient(mobD):
        if mobD.get("shotBy"):
            del mobD["shotBy"]
        return mobD

    def addMobile(self, options):
        newMob = Mobile(options)
        
        self.chunks.evaluateMob(newMob)
        self.gameState["mobiles"].append(newMob)

        return newMob

    def addPlayer(self, build):
        build = copy.deepcopy(self.BUILDS[build])
        newMob = Player({"pos":[random.random(),0],"radius":build["size"]*(0.2/15),"build":build,"team":"#f00"})
        
        self.chunks.evaluateMob(newMob)
        self.gameState["mobiles"].append(newMob)
        self.gameState["players"].append(newMob)

        return newMob

    def addClientPlayer(self, clientId):
        mob = self.addPlayer("pellet")
        mob.clientId = clientId

        return mob

    def killMobile(self, mob):
        if (mob.player):
            self.setMobilePosition(mob, [
                10,
                0+random.random()
            ])
            mob.health = 1
        else:
            mob.duration = 0
            self.chunks.evaluateMob(mob)
            self.deleteMobile(mob)

    def deleteMobile(self,mob):
        if mob in self.gameState["mobiles"]:
            self.gameState["mobiles"].remove(mob)
        self.chunks.removeMob(mob.chunkPos, mob)
            

    def updatePlayerCollisions(self,delta):
        for mobile1 in self.gameState["mobiles"]:
            nearbyMobiles = Chunks.getMobilesInChunks(
                self.chunks.getSurroundingChunks(mobile1.chunkPos)
            )
            for mobile2 in nearbyMobiles:
                if (mobile1.id!=mobile2.id):
                    dst = math.sqrt(math.pow(mobile1.pos[0]-mobile2.pos[0],2)+math.pow(mobile1.pos[1]-mobile2.pos[1],2))
                    totalRad = (mobile1.build["size"]*(0.2/15))+(mobile2.build["size"]*(0.2/15))
                    if (dst<totalRad):
                        
                        
                        #print(angle)
                        def procColl(mobile1, mobile2, mod=0.5):

                            angle = math.atan2(mobile1.pos[1]-mobile2.pos[1],mobile1.pos[0]-mobile2.pos[0])
                            magnitude = 5
                            strength = math.pow((max(-(dst-totalRad),0)*10)+1,2)*magnitude

                            isSelf =  (mobile1.shotBy==mobile2.shotBy or mobile1.id==mobile2.id)
                            isSameTeam = mobile1.team == mobile2.team
                            isHealingAttack = mobile2.build["bodyDamage"]<0 or mobile1.build["bodyDamage"]<0

                            isBulletOnBullet = mobile1.bullet and mobile2.bullet

                            
                            

                            damaging = (not isSelf) and ((isSameTeam) if (isHealingAttack and not isBulletOnBullet) else not isSameTeam)
                            if damaging:
                                damage = mobile2.build["bodyDamage"]*(50/3.5) if damaging else 0
                                mobile1.health = max(min(((mobile1.health*mobile1.build["maxHealth"]
                                )-(damage*delta*mod)
                                )/mobile1.build["maxHealth"],1),0)


                                if (mobile1.health<=0):
                                    self.killMobile(mobile1)
                                if (mobile2.health<=0):
                                    self.killMobile(mobile2)

                            if (False) if isBulletOnBullet else (not isSameTeam):

                                mobile1.vel[0] += math.cos(angle)*strength*delta * (mobile2.radius/mobile1.radius)
                                mobile1.vel[1] += math.sin(angle)*strength*delta * (mobile2.radius/mobile1.radius)

                        procColl(mobile1,mobile2)
                        procColl(mobile2,mobile1)


    def updatePlayerControls(self, delta):
        for player in self.gameState["players"]:

            if player.keys.get("mouseDown"):
                self.shoot(player, delta)


            moveV = [0,0]

            if player.keys.get(player.controls[0]):
                moveV[0]-=1
            if player.keys.get(player.controls[1]):
                moveV[0]+=1
            if player.keys.get(player.controls[2]):
                moveV[1]-=1
            if player.keys.get(player.controls[3]):
                moveV[1]+=1

            moveVD = math.sqrt(math.pow(moveV[0],2)+math.pow(moveV[1],2))!=0

            moveVA = math.atan2(moveV[0],moveV[1])
            moveVM = 8 * (1 if moveVD else 0) * player.build["speed"]
            moveV = [
                math.cos(moveVA)*moveVM,
                math.sin(moveVA)*moveVM
            ]

            player.vel[0] += moveV[0]*delta
            player.vel[1] += moveV[1]*delta
            
    def setMobilePosition(self, mob, pos, add=False):
        if add:
            mob.pos[0] += pos[0]
            mob.pos[1] += pos[1]
        else:
            mob.pos[0] = pos[0]
            mob.pos[1] = pos[1]

        if (mob.player or mob.bot):
            mob.pos[0] = max(min(mob.pos[0],10),-5)
            if (mob.pos[0]>=10 or mob.pos[0]<=-5):
                mob.vel[0] = 0
            if (mob.pos[1]>=10 or mob.pos[1]<=-5):
                mob.vel[1] = 0
            mob.pos[1] = max(min(mob.pos[1],10),-5)
        self.chunks.evaluateMob(mob)

    def updateState(self, delta):
        

        for mob in self.gameState["mobiles"]:
            mob.duration -= delta
            if (mob.duration<=0):
                self.deleteMobile(mob)
                continue

            if (mob.bot):
                runBot(self, mob, delta)
            if (mob.autoShoot):
                self.shoot(mob, delta)

            for gun in mob.build["guns"]:
                gun["shootCooldown"] = max(gun["shootCooldown"]-delta,-gun["startDelay"])

            

            self.setMobilePosition(mob, [
                mob.vel[0]*delta,
                mob.vel[1]*delta,
            ], add=True)
            


            mob.vel[0] *= math.pow(mob.friction, delta)
            mob.vel[1] *= math.pow(mob.friction, delta)


        self.updatePlayerCollisions(delta)

    def shoot(self, mob, delta, pos=False):
        for gun in mob.build["guns"]:
            if (gun["shootCooldown"] <= 0):
                gun["shootCooldown"] = min(gun["shootCooldown"]+delta*2,0)
            if (gun["shootCooldown"] == 0):
                gun["shootCooldown"] = gun["speed"]

                bulletBuild = gun["bullet"]["build"]

                nPos = [0,0]
                posAngle = (gun["pos"]*(math.pi/180))+mob.rotation
                posLength = (0.85*(gun["height"]/17))*(mob.build["size"]*(0.2/17))*2
                nPos[0] = mob.pos[0]+(math.cos(posAngle)*posLength)
                nPos[1] = mob.pos[1]+(math.sin(posAngle)*posLength)

                offset = gun["offset"]*(mob.build["size"]*(0.2/17))*2*2

                nPos[0] += (math.cos(posAngle+(math.pi*0.5))*offset)
                nPos[1] += (math.sin(posAngle+(math.pi*0.5))*offset)
                
                bulletMob = self.addMobile({
                    "radius":bulletBuild["size"]*(0.2/15),
                    "pos":pos if pos else nPos,
                    "build":bulletBuild,

                    "team":mob.team,
                })

                spreadRand = (random.randrange(-gun["spread"],gun["spread"]))*(math.pi/180)
                shootAngle = posAngle#+ spreadRand

                bulletSpeed = bulletBuild["speed"]*(6/8)
                bulletMob.vel = [
                    mob.vel[0]+(math.cos(shootAngle)*bulletSpeed),
                    mob.vel[1]+(math.sin(shootAngle)*bulletSpeed)
                ]


            
                bulletMob.autoShoot = gun["bullet"].get("autoShoot")
                bulletMob.rotation = shootAngle
                bulletMob.friction = 1
                bulletMob.duration = bulletBuild["duration"]/100

                bulletMob.shotBy = mob.shotBy
                bulletMob.bullet = True

                recoilStrength = (gun["recoilMod"]*(30/50)) * math.pow(bulletBuild["size"]/15,2)
                mob.vel = [
                    mob.vel[0]-(math.cos(posAngle)*recoilStrength),
                    mob.vel[1]-(math.sin(posAngle)*recoilStrength)
                ]
                
                #print(bulletMob.options)
                #print("shot")

    def explode(self):
        pass