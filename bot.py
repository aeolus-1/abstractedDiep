import math

def intercept(src, dst, v):
    tx = dst['x'] - src['x']
    ty = dst['y'] - src['y']
    tvx = dst['vx']
    tvy = dst['vy']

    # Get quadratic equation components
    a = tvx * tvx + tvy * tvy - v * v
    b = 2 * (tvx * tx + tvy * ty)
    c = tx * tx + ty * ty

    # Solve quadratic
    ts = quad(a, b, c)  # See quad() function below

    # Find smallest positive solution
    sol = None
    if ts:
        t0 = ts[0]
        t1 = ts[1]
        t = min(t0, t1)
        if t < 0:
            t = max(t0, t1)
        if t > 0:
            sol = {
                'x': dst['x'] + dst['vx'] * t,
                'y': dst['y'] + dst['vy'] * t
            }

    return sol

def quad(a, b, c):
    sol = None
    if abs(a) < 1e-6:
        if abs(b) < 1e-6:
            sol = [0, 0] if abs(c) < 1e-6 else None
        else:
            sol = [-c / b, -c / b]
    else:
        disc = b * b - 4 * a * c
        if disc >= 0:
            disc = math.sqrt(disc)
            a = 2 * a
            sol = [(-b - disc) / a, (-b + disc) / a]
    return sol



def runBot(self, bot, delta, movement=[0,0]):
    
    

    def makeMove(pos, dir=1):
        moveVM = self.getMobileSpeed(bot) * dir
        moveVA = math.atan2(pos[1]-bot.pos[1],pos[0]-bot.pos[0])
        
        moveV = [
            math.cos(moveVA)*moveVM,
            math.sin(moveVA)*moveVM
        ]

        bot.vel[0] += moveV[0]*delta
        bot.vel[1] += moveV[1]*delta

    def setLookAt(pos):
        bot.rotation = math.atan2(pos[1]-bot.pos[1],pos[0]-bot.pos[0])


    def findPlayers(a):
        return (a.player or a.bot) and a.id!=bot.id and a.shotBy!=bot.shotBy
    def findVisiblePlayers(a):
        return math.sqrt(math.pow(a.pos[0]-bot.pos[0],2)+math.pow(a.pos[1]-bot.pos[1],2)) < bot.build["sight"]*(10/600) and a.invis>0.1
    def sortPlayers(a):
        return math.sqrt(math.pow(a.pos[0]-bot.pos[0],2)+math.pow(a.pos[1]-bot.pos[1],2))

    totalPlayers = list(filter(findPlayers, self.gameState["mobiles"]))    
    visiblePlayers = list(filter(findVisiblePlayers, totalPlayers))    
    nearbyPlayers = list(sorted(visiblePlayers,key=sortPlayers))

    nearbyEnemies = []
    nearbyFriendlies = []

    for mob in nearbyPlayers:
        if (mob.team==bot.team):
            nearbyFriendlies.append(mob)
        else:
            nearbyEnemies.append(mob)

    def runAttackEnemy():
        target = nearbyEnemies[0]

        dst = math.sqrt(math.pow(target.pos[0]-bot.pos[0],2)+math.pow(target.pos[1]-bot.pos[1],2))

        if target.health-bot.health < 0.6:
            if (dst>bot.build["range"]*(10/600)):
                makeMove(target.pos)
            elif (dst<bot.build["range"]*(10/600)*0.85):
                makeMove(target.pos, -1)
        else:
            if (dst<8):
                makeMove(target.pos, -1)
            

        usedGun = bot.build["guns"]
        if len(usedGun):
            usedGun = usedGun[0]

            deflectionPos = intercept(
                {
                    "x":bot.pos[0],
                    "y":bot.pos[1],
                },
                {
                    "x":target.pos[0],
                    "y":target.pos[1],
                    "vx":target.vel[0]+bot.vel[0],
                    "vy":target.vel[1]+bot.vel[1],
                },
                usedGun["bullet"]["build"]["speed"]*(6/8)
            )
            
            if deflectionPos==None:
                return 0
            setLookAt([deflectionPos["x"],deflectionPos["y"]])
            


        self.shoot(bot, delta)

    def runHealFriend():
        def findLowestHealth(a):
            return a.health if a.health<0.9 else 1
        
        target = list(sorted(nearbyFriendlies,key=findLowestHealth))[0]

        dst = math.sqrt(math.pow(target.pos[0]-bot.pos[0],2)+math.pow(target.pos[1]-bot.pos[1],2))

        if target.health<0.9:

            usedGun = bot.build["guns"][0]

            deflectionPos = intercept(
                {
                    "x":bot.pos[0],
                    "y":bot.pos[1],
                },
                {
                    "x":target.pos[0],
                    "y":target.pos[1],
                    "vx":target.vel[0]+bot.vel[0],
                    "vy":target.vel[1]+bot.vel[1],
                },
                usedGun["bullet"]["build"]["speed"]*(6/8)
            )
            
            if deflectionPos==None:
                return 0
            setLookAt([deflectionPos["x"],deflectionPos["y"]])

            if (dst>1.5):
                makeMove(target.pos)
            if (dst<2):
                self.shoot(bot, delta)

            return False
        else:
            return True
            
        

    if bot.build.get("tracking"):
        if (len(nearbyFriendlies)>0):

            target = nearbyFriendlies[0]
            angle = math.atan2(target.pos[1]-bot.pos[1],target.pos[0]-bot.pos[0])

            bot.vel[0] += math.cos(angle)*delta*10
            bot.vel[1] += math.sin(angle)*delta*10
    else:
        if bot.build["healer"]:
            if len(nearbyFriendlies)>0:
                if runHealFriend():
                    if len(nearbyEnemies)>0:
                        runAttackEnemy()
            elif len(nearbyEnemies)>0:
                runAttackEnemy()
            else:
                pass
        else:
            if len(nearbyEnemies)>0:
                runAttackEnemy()
        
    
    