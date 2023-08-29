from mobile import Mobile
from chunks import Chunks
from bot import runBot
import math, json, random, copy, time

from mobile import *

POLYGON_DENSITY = 0.6 # how many polygons per metre squared should the game spawn
BOT_COUNT = 1 # what the game will try to keep the bot count at

GAME_BOUNDS = 25 # how many metres the game bounds are
POLY_SPAWNING_BIAS = 0.4 # bias towards the center of the map [0-1]

class Game:
    def __init__(self):
        self.options = {
            
        }
        self.gameState = {
            "mobiles":[],
            "players":[],
        }
        self.BUILDS = json.load(open('builds.json'))
        self.EFFECTS = json.load(open('effects.json'))

        self.chunks = Chunks({
            "chunkSize":[0.5,0.5],
        })

        self.gameBounds = [GAME_BOUNDS,GAME_BOUNDS]
        self.initTime = time.time()

        self.NAMES = json.load(open('names.json'))

        if True:
            
            pass
            #botMob.bot = True
            #self.spawnSparsePolys(50)
                
    def debugPrint(self, msg):
        print(f'[{round((time.time()-self.initTime)*10)/10}] {msg}')

    def spawnSparsePolys(self, num):
        for i in range(num):
            def bias(t, n):
                e = (1 - n) ** 3
                return (t * e) / (t * e - t + 1)

            xSign = ((random.randrange(0,2)*2)-1)
            ySign = ((random.randrange(0,2)*2)-1)

            biasNum = POLY_SPAWNING_BIAS

            pos = [
                (self.gameBounds[0]*0.5)+-5+bias(random.random(), biasNum)*xSign*self.gameBounds[0]*0.5,
                (self.gameBounds[1]*0.5)+-5+bias(random.random(), biasNum)*ySign*self.gameBounds[1]*0.5
            ]

            if random.random()>0.5:
                if random.random()>0.7:
                    botMob = self.addMobile({
                        "pos":pos,
                        "radius":0.4,
                        "build":self.BUILDS["pentagon"],

                        "team":"#7c8ef5",
                    })
                    botMob.poly = True
                    botMob.rotation = random.random()*math.pi*2
                    self.debugPrint("spawning pentagon")
                else:
                    botMob = self.addMobile({
                        "pos":pos,
                        "radius":0.25,
                        "build":self.BUILDS["triangle"],

                        "team":"#ea7e7a",
                    })
                    botMob.poly = True
                    botMob.rotation = random.random()*math.pi*2
                    self.debugPrint("spawning triangle")
            else:
                botMob = self.addMobile({
                    "pos":pos,
                    "radius":0.25,
                    "build":self.BUILDS["cube"],

                    "team":"#fae97c",
                })
                botMob.poly = True
                botMob.rotation = random.random()*math.pi*2
                self.debugPrint("spawning cube")

    def runCommand(self, code):
        eval(code)
    
    def spawnRandomBot(self):
        botMob = self.addMobile({
            "pos":[(random.random()*20)-5,(random.random()*20)-5],
            "radius":0.25,
            "build":self.BUILDS[random.choice(list(self.BUILDS.keys()))],

            "team":["#de5a57","#65dc76","#50b0dd","#b683ee"][random.randrange(0,3)],
        })
        botMob.username = random.choice(self.NAMES).split(",")[0]
        self.debugPrint("spawning random bot")
        botMob.bot = True
    
    def giveXp(self, num):
        if len(self.gameState["players"])>0:
            self.gameState["players"][0].xp += num

    def setBuild(self, mob, buildname):
        mob.build = copy.deepcopy(self.BUILDS[buildname])

    def fetchMobile(self, id):
        def filterC(a):
            return a.id==id
        mobs = list(filter(filterC,self.gameState["mobiles"]))

        if (len(mobs)>0):
            return mobs[0]
        else:
            raise "searched for mob that wasn't there"

    def getLeaderboard(self):
        leaders = []
        for i in self.gameState["mobiles"]:
            if i.bot or i.player:
                leaders.append(i)
        players = leaders
        returnDict = {}

        for player in players:
            returnDict[player.username] = player.xp

        return returnDict

    def getStateForClients(self, sid):
        state = {
            "mobiles":[],
            "players":[],
            "cameraPos":[0,0],
            "sight":100,
            "team":"#000",
            "leaderboard":{},
            "xp":9999,

            "timestamp":time.time()*1000
        }
        state["cameraPos"] = self.clients[sid]["mobile"].pos
        state["sight"] = self.clients[sid]["mobile"].build["sight"]
        state["team"] = self.clients[sid]["mobile"].team
        state["bounds"] = self.gameBounds
        state["xp"] = self.clients[sid]["mobile"].xp
        state["leaderboard"] = self.getLeaderboard()
        totMobiles = self.chunks.getAllMobiles()

        for mob in totMobiles:
            preSize = copy.copy(mob.build["size"])
            mob.build["size"] = self.getMobileSize(mob)
            if (mob.player):
                state["players"].append(Game.processMobDictForClient(copy.deepcopy(mob.__dict__)))
            else:
                state["mobiles"].append(Game.processMobDictForClient(copy.deepcopy(mob.__dict__)))
            mob.build["size"] = preSize

        return state

    def getStateForSpectator(self):
        state = {
            "mobiles":[],
            "players":[],
            "cameraPos":[0,0],
            "sight":1000,
            "team":"#fff",
            "leaderboard":{},

            "timestamp":time.time()*1000
        }
        state["leaderboard"] = self.getLeaderboard()
        bots = []
        players = []
        totMobiles = self.chunks.getAllMobiles()
        for mob in totMobiles:
            if (mob.bot):
                bots.append(mob)
            if mob.player:
                players.append(mob)


        target = players[0] if len(players)>0 else (bots[0] if len(bots)>0 else None)
        if target != None:
            state["cameraPos"] = target.pos
            state["xp"] = target.xp
        state["bounds"] = self.gameBounds
        totMobiles = self.chunks.getAllMobiles()

        for mob in totMobiles:
            preSize = copy.copy(mob.build["size"])
            mob.build["size"] = self.getMobileSize(mob)
            if (mob.player):
                state["players"].append(Game.processMobDictForClient(copy.deepcopy(mob.__dict__)))
            else:
                state["mobiles"].append(Game.processMobDictForClient(copy.deepcopy(mob.__dict__)))
            mob.build["size"] = preSize

        return state

    def processMobDictForClient(mobD):
        if mobD.get("shotBy"):
            del mobD["shotBy"]
            mobD["drones"] = []
        return mobD

    def addMobile(self, options):
        newMob = Mobile(options)
        
        self.chunks.evaluateMob(newMob)
        self.gameState["mobiles"].append(newMob)

        return newMob

    def addPlayer(self, build, team="#f00"):
        build = copy.deepcopy(self.BUILDS[build])
        newMob = Player({"pos":[random.random(),0],"radius":self.getMobileSize(type('obj', (object,), {"build":build,"xp":0})),"build":build,"team":team})
        
        self.chunks.evaluateMob(newMob)
        self.gameState["mobiles"].append(newMob)
        self.gameState["players"].append(newMob)

        return newMob

    def addClientPlayer(self, clientId, data):
        if self.BUILDS.get(data["class"])==None:
            data["class"] = "starter"
        mob = self.addPlayer(data["class"], team=data["team"])
        mob.clientId = clientId

        return mob

    def killMobile(self, mob):
        for i in range(len(mob.drones)):
            mob.drones[0].duration = 0
            mob.drones.pop(0)
        if (mob.player and not hasattr(mob, "disconnected")):
            self.setMobilePosition(mob, [
                10,
                0+random.random()
            ])
            mob.xp = 0
            mob.health = 1
            mob.effects = {}
        else:
            if (mob.build.get("explodes")):
                self.explode(mob, mob.build["explodes"])
            mob.duration = 0
            #self.chunks.evaluateMob(mob)
            #self.deleteMobile(mob)

    def deleteMobile(self,mob):
        if mob in self.gameState["mobiles"]:
            self.gameState["mobiles"].remove(mob)
        if mob in self.gameState["players"]:
            self.gameState["players"].remove(mob)
        self.chunks.removeMob(mob.chunkPos, mob)
            
    def updatePlayerCollisions(self,delta):
        for mobile1 in self.gameState["mobiles"]:
            nearbyMobiles = Chunks.getMobilesInChunks(
                self.chunks.getSurroundingChunks(mobile1.chunkPos)
            )
            for mobile2 in nearbyMobiles:

                if (mobile1.id!=mobile2.id and mobile2.duration>0):
                    dst = math.sqrt(math.pow(mobile1.pos[0]-mobile2.pos[0],2)+math.pow(mobile1.pos[1]-mobile2.pos[1],2))
                    totalRad = (self.getMobileSize(mobile1))+(self.getMobileSize(mobile2))
                    
                    if (dst<totalRad):
                        if False:
                            intersect = max(totalRad-dst,0)*0.5
                            angle = math.atan2(mobile1.pos[1]-mobile2.pos[1],mobile1.pos[0]-mobile2.pos[0])
                            mod = self.getMobileSize(mobile1)/((self.getMobileSize(mobile1))+(self.getMobileSize(mobile2)))

                            mob1PushBack = intersect*mod
                            mob2PushBack = intersect*(1-mod)


                            mobile1.pos[0] += math.cos(angle)*mob1PushBack
                            mobile1.pos[1] += math.sin(angle)*mob1PushBack
                            
                            mobile2.pos[0] -= math.cos(angle)*mob2PushBack
                            mobile2.pos[1] -= math.sin(angle)*mob2PushBack

                        
                        
                        if True:
                            #print(angle)
                            def procColl(mobile1, mobile2, mod=0.5):

                                angle = math.atan2(mobile1.pos[1]-mobile2.pos[1],mobile1.pos[0]-mobile2.pos[0])
                                magnitude = 10
                                intersecPer = (max((totalRad-dst),0)/totalRad)
                                strength = min(1/(0.8+-(intersecPer*0.8)),50)*magnitude#math.pow((intersecPer)*3+1, 2)*magnitude

                                isSelf =  (mobile1.shotBy==mobile2.shotBy or mobile1.id==mobile2.id)
                                isSameTeam = mobile1.team == mobile2.team
                                isHealingAttack = mobile2.build["bodyDamage"]<0 or mobile1.build["bodyDamage"]<0

                                isBulletOnBullet = mobile1.bullet and mobile2.bullet

                                
                                

                                damaging = (not isSelf) and ((isSameTeam) if (isHealingAttack and not isBulletOnBullet) else not isSameTeam)
                                if damaging:
                                    damage = (mobile2.build["bodyDamage"]*(50/3.5) * (mobile2.build["bonusPolyDamage"] if mobile2.build.get("bonusPolyDamage") else 1)  )  if damaging else 0
                                    mobile1.health = max(min(((mobile1.health*mobile1.build["maxHealth"]
                                    )-(damage*delta*mod)
                                    )/mobile1.build["maxHealth"],1),0)

                                    if damage>0:
                                        mobile1.lastDamaged = (time.time())

                                    if (mobile2.build.get("bodyEffects")):
                                        for effect in mobile2.build["bodyEffects"]:
                                            mobile1.effects[effect] = copy.deepcopy(self.EFFECTS[effect])
                                            
                                    


                                    if (mobile1.health<=0):
                                        if not mobile1.bullet:
                                            self.debugPrint("mobile killed")
                                        givenXp = mobile1.build["xp"] if mobile1.poly else (150 if not mobile1.bullet else 0)
                                        mobile2.shotBy.xp += givenXp + mobile1.xp
                                        
                                        self.killMobile(mobile1)
                                    

                                if ((False) if isBulletOnBullet else (not isSameTeam)) or mobile1.build.get("drone"):
                                    totrad = mobile1.radius+mobile2.radius
                                    mobile1.vel[0] += math.cos(angle)*strength*delta * (mobile2.radius/totrad)
                                    mobile1.vel[1] += math.sin(angle)*strength*delta * (mobile2.radius/totrad)

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
            moveVM = (1 if moveVD else 0) * self.getMobileSpeed(player)
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

        if (not mob.bullet):
            mob.pos[0] = max(min(mob.pos[0],self.gameBounds[0]-5),-5)
            if (mob.pos[0]>=self.gameBounds[0]-5 or mob.pos[0]<=-5):
                mob.vel[0] = 0
            if (mob.pos[1]>=self.gameBounds[1]-5 or mob.pos[1]<=-5):
                mob.vel[1] = 0
            mob.pos[1] = max(min(mob.pos[1],self.gameBounds[1]-5),-5)
        
        if (mob.bullet):
            angle = math.atan2(mob.vel[1],mob.vel[0])
            dst = min(math.sqrt((math.pow(mob.vel[0],2))+math.pow(mob.vel[1],2)), mob.build["speed"]*(6/8))

            mob.vel[0] = math.cos(angle)*dst
            mob.vel[1] = math.sin(angle)*dst

        
        self.chunks.evaluateMob(mob)

    def updateState(self, delta):
        

        actives = 0
        polys = 0

        for mob in self.gameState["mobiles"]:
            mob.duration -= delta
            if (mob.opacity<=0):
                mob.delete = True
                if (mob.build.get("explodes")):
                    self.explode(mob, mob.build["explodes"])
                self.deleteMobile(mob)
            if (mob.delete):
                self.deleteMobile(mob)
                continue

            self.setMobilePosition(mob, [
                mob.vel[0]*delta,
                mob.vel[1]*delta,
            ], add=True)
            mob.rotation = math.atan2(mob.target[1],mob.target[0])

            if mob.drones:
                off = 0
                for i in range(len(mob.drones)):
                    if mob.drones[i-off].duration<=0:
                        mob.drones.pop(i-off)
                        off += 1

            

            if (mob.duration<=0):
                mob.opacity -= delta * (4.5/1)
                continue

            timeSinceDamaged = (time.time())-mob.lastDamaged
            if timeSinceDamaged>(mob.regenerationTime * (2.5 if mob.poly else 1)):
                mob.health += 0.1*delta

            velDst = math.sqrt(math.pow(mob.vel[0],2)+math.pow(mob.vel[1],2))
            if mob.build.get("invisible"):
                if (velDst>1):
                    mob.invis = mob.build.get("invisible")
                else:
                    mob.invis -= delta
            
            deletions = []
            for effName in mob.effects:
                effect = mob.effects[effName]
                effect["duration"] = max(effect["duration"]-delta,0)
                if (effect["duration"]<=0):
                    deletions.append(effName)
                    continue

                if effect.get("health"):
                    mob.health += effect["health"]*delta
                    if (effect["health"]<0):
                        mob.lastDamaged = (time.time())

            for i in deletions:
                del mob.effects[i]

            if mob.bot:
                actives += 1
            if mob.poly:
                polys += 1

            if (mob.bot or mob.build.get("tracking") or mob.build.get("drone")):
                runBot(self, mob, delta)
                
            if (mob.autoShoot):
                self.shoot(mob, delta)
            

            for gun in mob.build["guns"]:
                gun["shootCooldown"] = max(gun["shootCooldown"]-delta,-gun["startDelay"])

            

            
            


            mob.vel[0] *= math.pow(mob.friction, delta)
            mob.vel[1] *= math.pow(mob.friction, delta)

        if (actives<BOT_COUNT):
            self.spawnRandomBot()

        if polys<(self.gameBounds[0]*self.gameBounds[1])*(POLYGON_DENSITY/18):
            self.spawnSparsePolys(1)

        self.updatePlayerCollisions(delta)

    def shoot(self, mob, delta, pos=False):
        for gun in mob.build["guns"]:
            if (gun["shootCooldown"] <= 0):
                gun["shootCooldown"] = min(gun["shootCooldown"]+delta*2,0)
            if (gun["shootCooldown"] == 0):
                gun["shootCooldown"] = gun["speed"]

                bulletBuild = gun["bullet"]["build"]

                isDrone = False

                if bulletBuild.get("drone"):
                    if bulletBuild["drone"] and len(mob.shotBy.drones)<mob.shotBy.build["droneCount"]:
                        isDrone = True
                    else:
                        return 0

                nPos = [0,0]
                posAngle = (gun["pos"]*(math.pi/180))+mob.rotation
                posLength = (0.85*(gun["height"]/17))*self.getMobileSize(mob)
                nPos[0] = mob.pos[0]+(math.cos(posAngle)*posLength)
                nPos[1] = mob.pos[1]+(math.sin(posAngle)*posLength)

                offset = gun["offset"]*self.getMobileSize(mob)*2*2

                nPos[0] += (math.cos(posAngle+(math.pi*0.5))*offset)
                nPos[1] += (math.sin(posAngle+(math.pi*0.5))*offset)
                
                
                bulletMob = self.addMobile({
                    "radius":self.getMobileSize(mob),
                    "pos":pos if pos else nPos,
                    "build":bulletBuild,

                    "team":mob.team,
                })

                spreadRand = (random.randrange(-gun["spread"],gun["spread"]))*(math.pi/180)
                shootAngle = posAngle#+ spreadRand

                bulletSpeed = bulletBuild["speed"]*(6/8)
                bulletMob.vel = [
                    (math.cos(shootAngle)*bulletSpeed),
                    (math.sin(shootAngle)*bulletSpeed)
                ]


            
                bulletMob.autoShoot = gun["bullet"].get("autoShoot")
                bulletMob.rotation = shootAngle
                bulletMob.friction = bulletBuild["friction"]
                bulletMob.duration = bulletBuild["duration"]/100

                bulletMob.shotBy = mob.shotBy
                bulletMob.bullet = True

                if isDrone:
                    mob.shotBy.drones.append(bulletMob)

                

                recoilStrength = (gun["recoilMod"]*(30/50)) * math.pow(bulletBuild["size"]/15,2)
                
                mob.vel = [
                    mob.vel[0]-(math.cos(posAngle)*recoilStrength),
                    mob.vel[1]-(math.sin(posAngle)*recoilStrength)
                ]
                
                #print(bulletMob.options)
                #print("shot")

    def getMobileSpeed(self,mob):
        totSpeed = 1
        for effect in mob.effects:
            effect = mob.effects[effect]
            if effect.get("slow"):
                totSpeed *= effect["slow"]
            if effect.get("speed"):
                totSpeed *= effect["speed"]

        return mob.build["speed"] * 8 * totSpeed

    def getMobileSize(self,mob, mod=1):
        xpRate = 2000
        return mob.build["size"]* (0.2/15) #* (1 + (mod*(mob.xp/xpRate)))

    def explode(self, mob, explo):
        if not hasattr(mob,"exploded"):
            mob.exploded = True
            for angleN in range(explo["num"]):
                angle = ((angleN/explo["num"])*math.pi*2)

                bulletBuild = explo["bullet"]["build"]

                bulletMob = self.addMobile({
                    "radius":self.getMobileSize(self.getMobileSize(type('obj', (object,), {"build":explo["bullet"],"xp":0}))),
                    "pos":copy.deepcopy(mob.pos),
                    "build":bulletBuild,

                    "team":mob.team,
                })

                
                shootAngle = angle#+ spreadRand

                bulletSpeed = bulletBuild["speed"]*(6/8)
                bulletMob.vel = [
                    (math.cos(shootAngle)*bulletSpeed),
                    (math.sin(shootAngle)*bulletSpeed)
                ]


            
                bulletMob.autoShoot = explo["bullet"].get("autoShoot")
                bulletMob.rotation = shootAngle
                bulletMob.friction = 1
                bulletMob.duration = bulletBuild["duration"]/100

                bulletMob.shotBy = mob.shotBy
                bulletMob.bullet = True
