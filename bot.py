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



def runBot(self, bot):
    def sortPlayers(a):
        return math.sqrt(math.pow(a.pos[0]-bot.pos[0],2)+math.pow(a.pos[1]-bot.pos[1],2))
        
    nearbyPlayers = list(sorted(self.gameState["players"],key=sortPlayers))
    if len(nearbyPlayers)>0:
        target = nearbyPlayers[0]
        

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
                usedGun["bullet"]["build"]["speed"]*(3/8)
            )

            angleToNearby = math.atan2(bot.pos[1]-deflectionPos["y"],bot.pos[0]-deflectionPos["x"])+math.pi
            bot.rotation = angleToNearby


        self.shoot(bot)
