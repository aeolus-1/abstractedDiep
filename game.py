from mobile import Mobile
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


        botMob = self.addMobile({
            "pos":[-1,0],
            "radius":0.25,
            "build":self.BUILDS["starter"],

            "team":"#f00",
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
            "cameraPos":[0,0]
        }
        state["cameraPos"] = self.clients[sid]["mobile"].pos
        for mob in self.gameState["mobiles"]:
            if (mob.player):
                state["players"].append(mob.__dict__)
            else:
                state["mobiles"].append(mob.__dict__)

        return state

    def addMobile(self, options):
        newMob = Mobile(options)
        
        self.gameState["mobiles"].append(newMob)

        return newMob

    def addPlayer(self, build):
        build = copy.deepcopy(self.BUILDS[build])
        newMob = Player({"pos":[random.random(),0],"radius":build["size"]*(0.2/15),"build":build,"team":"#0f0"})
        
        self.gameState["mobiles"].append(newMob)
        self.gameState["players"].append(newMob)

        return newMob

    def addClientPlayer(self, clientId):
        mob = self.addPlayer("starter")
        mob.clientId = clientId

        return mob

    def killMobile(self, mob):
        if (mob.player):
            mob.pos = [10,0]
            mob.health = 1
        else:
            mob.duration = 0
            

    def updatePlayerCollisions(self,delta):
        for mobile1 in self.gameState["mobiles"]:
            for mobile2 in self.gameState["mobiles"]:
                if (mobile1.id!=mobile2.id):
                    dst = math.sqrt(math.pow(mobile1.pos[0]-mobile2.pos[0],2)+math.pow(mobile1.pos[1]-mobile2.pos[1],2))
                    totalRad = (mobile1.build["size"]*(0.2/15))+(mobile2.build["size"]*(0.2/15))
                    if (dst<totalRad):
                        angle = math.atan2(mobile1.pos[1]-mobile2.pos[1],mobile1.pos[0]-mobile2.pos[0])
                        magnitude = 1
                        strength = math.pow((max(-(dst-totalRad),0)*10)+1,2)*magnitude
                        
                        #print(angle)

                        damaging = mobile1.team != mobile2.team
                        
                        mobile1.vel[0] += math.cos(angle)*strength*delta * (mobile2.radius/mobile1.radius)
                        mobile1.vel[1] += math.sin(angle)*strength*delta * (mobile2.radius/mobile1.radius)

                        damage = mobile2.build["bodyDamage"]*(50/3.5) if damaging else 0
                        mobile1.health = ((mobile1.health*mobile1.build["maxHealth"]
                        )-(damage*delta)
                        )/mobile1.build["maxHealth"]

                        
                        mobile2.vel[0] -= math.cos(angle)*strength*delta * (mobile1.radius/mobile2.radius)
                        mobile2.vel[1] -= math.sin(angle)*strength*delta * (mobile1.radius/mobile2.radius)

                        damage = mobile1.build["bodyDamage"]*(50/3.5) if damaging else 0
                        mobile2.health = ((mobile2.health*mobile2.build["maxHealth"]
                        )-(damage*delta)
                        )/mobile2.build["maxHealth"]

                        if (mobile1.health<=0):
                            self.killMobile(mobile1)
                        if (mobile2.health<=0):
                            self.killMobile(mobile2)



    def updatePlayerControls(self, delta):
        for player in self.gameState["players"]:

            if player.keys.get("mouseDown"):
                self.shoot(player)


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
            

    def updateState(self, delta):
        

        for mob in self.gameState["mobiles"]:
            mob.duration -= delta
            if (mob.duration<=0):
                self.gameState["mobiles"].remove(mob)
                continue

            if (mob.bot):
                runBot(self, mob)

            for gun in mob.build["guns"]:
                gun["shootCooldown"] = max(gun["shootCooldown"]-delta,0)

            

            mob.pos[0] += mob.vel[0]*delta
            mob.pos[1] += mob.vel[1]*delta

            mob.vel[0] *= math.pow(mob.friction, delta)
            mob.vel[1] *= math.pow(mob.friction, delta)

        self.updatePlayerControls(delta)

        self.updatePlayerCollisions(delta)

    def shoot(self, mob, pos=False):
        for gun in mob.build["guns"]:
            if (gun["shootCooldown"] <= 0):
                gun["shootCooldown"] = gun["speed"]/1000

                bulletBuild = gun["bullet"]["build"]

                nPos = [0,0]
                posAngle = (gun["pos"]*(math.pi/180))+mob.rotation
                posLength = (0.85*(gun["height"]/17))*(mob.build["size"]*(0.2/17))*2
                nPos[0] = mob.pos[0]+(math.cos(posAngle)*posLength)
                nPos[1] = mob.pos[1]+(math.sin(posAngle)*posLength)
                
                bulletMob = self.addMobile({
                    "radius":bulletBuild["size"]*(0.2/15),
                    "pos":pos if pos else nPos,
                    "build":bulletBuild,

                    "team":mob.team,
                })

                bulletSpeed = bulletBuild["speed"]*(3/8)
                bulletMob.vel = [
                    mob.vel[0]+(math.cos(posAngle)*bulletSpeed),
                    mob.vel[1]+(math.sin(posAngle)*bulletSpeed)
                ]
                bulletMob.friction = 1
                bulletMob.duration = bulletBuild["duration"]/100
                
                #print(bulletMob.options)
                #print("shot")
